import os
from functools import wraps
import datetime

import requests
from babel import Locale
from flask import Flask, render_template, request, abort, Markup, g
from flask_babel import Babel, gettext, get_locale
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, validators, FloatField

app = Flask(__name__, static_url_path="/geo/static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["NCZI_TOKEN"] = os.environ.get("NCZI_TOKEN")
app.config["SLACK_HOOK"] = os.environ.get("SLACK_HOOK", None)

csrf = CSRFProtect(app)

babel = Babel(app, default_locale="sk", default_timezone="Europe/Bratislava")
translations = babel.list_translations() + [Locale("sk")]
app.jinja_env.globals["get_locale"] = get_locale
app.jinja_env.globals["translations"] = translations
app.jinja_env.globals["accuracy_bound"] = 25
app.jinja_env.globals["accuracy_timeout"] = 5 * 60 * 1000
app.jinja_env.policies["ext.i18n.trimmed"] = True

if app.env == "production":
    print("!! PROD PROD PROD PROD PROD PROD PROD PROD PROD PROD PROD PROD !!")


@babel.localeselector
def localeselector():
    if hasattr(g, "lang"):
        return g.lang
    return None


def lang_supported(f):
    @wraps(f)
    def wrapper(lang, token):
        lang_code = lang
        for locale in translations:
            if lang == locale.language:
                break
        else:
            lang_code = "sk"
        g.lang = lang_code
        return f(lang_code, token)

    return wrapper


class LocationForm(FlaskForm):
    token = StringField("token", [validators.required(), validators.length(min=32, max=32)])
    lat = FloatField("lat", [validators.required()])
    lng = FloatField("lng", [validators.required()])
    street = StringField("street", [validators.required(), validators.length(max=150)])
    street_number = StringField("street_number", [validators.required(), validators.length(max=25)])
    city = StringField("city", [validators.required(), validators.length(max=150)])
    zip = StringField("psc", [validators.required(), validators.length(max=7)])


def submit_form(form):
    if app.env == "production":
        endpoint = "https://mojeezdravie.nczisk.sk/api/v1/sq/quarantine-geo-location"
    else:
        endpoint = "https://t.mojeezdravie.sk/api/v1/sq/quarantine-geo-location"
    data = {
        "vOneTimeToken": form.token.data,
        "nQuarantineAddressLatitude": form.lat.data,
        "nQuarantineAddressLongitude": form.lng.data,
        "vQuarantineAddressCountry": "SK",
        "vQuarantineAddressStreetName": form.street.data,
        "vQuarantineAddressStreetNumber": form.street_number.data,
        "vQuarantineAddressCity": form.city.data,
        "vQuarantineAddressCityZipCode": form.zip.data
    }
    headers = {
        "Authorization": "Bearer " + app.config["NCZI_TOKEN"]
    }

    resp = requests.post(endpoint, json=data, headers=headers)
    if app.env == "development":
        print(data, headers)
        print(resp.status_code, resp.content)
    if app.config["SLACK_HOOK"]:
        try:
            if resp.status_code == 200:
                template = ":world_map: Na doméne ekarantena.korona.gov.sk si zmenil polohu repatriant s tokenom *{}*, čas: *{}*, mesto: *{}*, response: *{}* :heavy_check_mark:"
            else:
                template = ":world_map: Na doméne ekarantena.korona.gov.sk skúsil zmeniť polohu repatriant s tokenom *{}*, čas: *{}*, mesto: *{}*, response: *{}* :x:"
            slack = {
                "text": template.format(form.token.data[:5], datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), form.city.data, resp.status_code)
            }
            requests.post(app.config["SLACK_HOOK"], json=slack)
        except:
            pass
    ok = True
    message = ""
    detail = ""
    again = True
    if resp.status_code == 200:
        message = gettext("Poloha domácej izolácie bola úspešne aktualizovaná.")
        again = False
    elif resp.status_code == 202:
        ok = False
        message = gettext("Chyba")
        again = False
        try:
            resp_data = resp.json()
            detail = resp_data["errors"][0]["description"]
        except Exception:
            detail = gettext("Poloha domácej izolácie už bola raz aktualizovaná.")
    elif resp.status_code == 400:
        ok = False
        message = gettext("Chyba. Bad request.")
        detail = ""
        again = True
    elif resp.status_code == 404:
        ok = False
        message = gettext("Chyba")
        detail = Markup(gettext("Platnosť linku na spresnenie polohy domácej izolácie vypršala. Vyčkajte na ďalšiu výzvu na spresnenie polohy vašej domácej izolácie."))
        again = False
    elif resp.status_code == 401:
        ok = False
        message = gettext("Chyba. Unauthorized.")
        again = True
    elif resp.status_code == 403:
        ok = False
        message = gettext("Chyba. Forbidden.")
        again = True
    return resp, ok, message, detail, again


@app.route("/geo/<string:token>", defaults={"lang": "sk"})
@app.route("/geo/<string:lang>/<string:token>")
@lang_supported
def landing(lang, token):
    if len(token) != 32:
        abort(404)
    return render_template("landing.html.jinja2", token=token)


@app.route("/geo/<string:token>/do", defaults={"lang": "sk"}, methods=["GET", "POST"])
@app.route("/geo/<string:lang>/<string:token>/do", methods=["GET", "POST"])
@lang_supported
def locate(lang, token):
    if len(token) != 32:
        abort(404)
    form = LocationForm()
    if request.method == "GET":
        form.token.data = token
        return render_template("locate.html.jinja2", token=token, form=form)
    elif form.validate_on_submit():
        resp, ok, message, detail, again = submit_form(form)
        return render_template("located.html.jinja2", token=token, message=message,
                               detail=detail, ok=ok, errors={}, again=again)
    else:
        return render_template("located.html.jinja2", token=token, message=gettext("Chyba."),
                               detail=None, ok=False, errors=form.errors, again=True)


@app.errorhandler(404)
def error(error):
    return render_template("error.html.jinja2", message=str(error.code), detail=error.description)
