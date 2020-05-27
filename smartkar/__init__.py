import os

import requests
from flask import Flask, render_template, request, abort, Markup
from flask_babel import Babel, gettext, lazy_gettext
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, validators, FloatField

app = Flask(__name__, static_url_path="/geo/static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["NCZI_TOKEN"] = os.environ.get("NCZI_TOKEN")
app.jinja_env.policies["ext.i18n.trimmed"] = True

csrf = CSRFProtect(app)

babel = Babel(app, default_locale="sk", default_timezone="Europe/Bratislava")

try:
    os.makedirs(app.instance_path)
except OSError:
    pass


@babel.localeselector
def get_locale():
    if "lang" in request.args:
        return request.args.get("lang")
    return None


class PlaceForm(FlaskForm):
    token = StringField("token", [validators.required(), validators.length(min=32, max=32)])
    lat = FloatField("lat", [validators.required()])
    lng = FloatField("lng", [validators.required()])


class AddressForm(FlaskForm):
    token = StringField("token", [validators.required(), validators.length(min=32, max=32)])
    street = StringField("street", [validators.required(), validators.length(max=150)])
    street_number = StringField("street_number", [validators.required(), validators.length(max=25)])
    city = StringField("city", [validators.required(), validators.length(max=150)])
    zip = StringField("psc", [validators.required(), validators.length(max=7)])


class BothForm(FlaskForm):
    token = StringField("token", [validators.required(), validators.length(min=32, max=32)])
    lat = FloatField("lat", [validators.required()])
    lng = FloatField("lng", [validators.required()])
    street = StringField("street", [validators.required(), validators.length(max=150)])
    street_number = StringField("street_number", [validators.required(), validators.length(max=25)])
    city = StringField("city", [validators.required(), validators.length(max=150)])
    zip = StringField("psc", [validators.required(), validators.length(max=7)])


types = {
    "a": {
        "nominativ": lazy_gettext("adresa"),
        "genitiv": lazy_gettext("adresy"),
        "dativ": lazy_gettext("adrese"),
        "akuzativ": lazy_gettext("adresu"),
        "lokal": lazy_gettext("adrese"),
        "instrumental": lazy_gettext("adresou")
    },
    "p": {
        "nominativ": lazy_gettext("poloha"),
        "genitiv": lazy_gettext("polohy"),
        "dativ": lazy_gettext("polohe"),
        "akuzativ": lazy_gettext("polohu"),
        "lokal": lazy_gettext("polohe"),
        "instrumental": lazy_gettext("polohou")
    },
    "b": {
        "nominativ": lazy_gettext("adresa a apoloha"),
        "genitiv": lazy_gettext("adresy a polohy"),
        "dativ": lazy_gettext("adrese a polohe"),
        "akuzativ": lazy_gettext("adresu a polohu"),
        "lokal": lazy_gettext("adrese a polohe"),
        "instrumental": lazy_gettext("adresou a polohou")
    }
}
# Nominativ - kto, co
# Genitiv - koho, coho
# Dativ - komu, comu
# Akuzativ -
# Lokal - o kom, o com
# Instrumental - s kym, s cim


forms = {
    "a": AddressForm,
    "p": PlaceForm,
    "b": BothForm
}


def submit_form(form):
    if app.env == "production":
        endpoint = "https://mojeezdravie.nczisk.sk/api/v1/sq/quarantine-geo-location"
    else:
        endpoint = "https://t.mojeezdravie.sk/api/v1/sq/quarantine-geo-location"
    data = {
        "vOneTimeToken": form.token.data
    }
    if isinstance(form, (PlaceForm, BothForm)):
        data["nQuarantineAddressLatitude"] = form.lat.data
        data["nQuarantineAddressLongitude"] = form.lng.data
    if isinstance(form, (AddressForm, BothForm)):
        data["vQuarantineAddressCountry"] = "SK"
        data["vQuarantineAddressStreetName"] = form.street.data
        data["vQuarantineAddressStreetNumber"] = form.street_number.data
        data["vQuarantineAddressCity"] = form.city.data
        data["vQuarantineAddressCityZipCode"] = form.zip.data
    headers = {
        "Authorization": "Bearer " + app.config["NCZI_TOKEN"]
    }
    print(data)
    print(headers)
    resp = requests.post(endpoint, json=data, headers=headers)
    print(resp.status_code)
    print(resp.content)
    ok = True
    message = ""
    detail = ""
    if resp.status_code == 200:
        message = gettext("Poloha domácej izolácie bola úspešne aktualizovaná.")
    elif resp.status_code == 202:
        ok = False
        try:
            resp_data = resp.json()
            message = gettext("Chyba. Duplicate.")
            detail = resp_data["ErrorText"]
        except Exception:
            message = gettext("Chyba. Duplicate.")
            detail = gettext("Poloha domácej izolácie už bola raz aktualizovaná.")
    elif resp.status_code == 400:
        ok = False
        message = gettext("Chyba. Bad request.")
        detail = ""
    elif resp.status_code == 404:
        ok = False
        message = gettext("Chyba. Nesprávny token.")
        detail = Markup(gettext(
                "Skontrolujte, že adresa stránky je správna a token <pre>{token}</pre> neobsahuje chybu.").format(
                token=Markup.escape(form.token.data)))
    elif resp.status_code == 401:
        ok = False
        message = gettext("Chyba. Unauthorized.")
    elif resp.status_code == 403:
        ok = False
        message = gettext("Chyba. Forbidden.")
    return resp, ok, message, detail


@app.route("/geo/<string:token>", defaults={"type": "b"})
# @app.route("/geo/<string:type>/<string:token>")
def landing(type, token):
    if type not in types or len(token) != 32:
        abort(404)
    return render_template("landing.html.jinja2", type=type, type_name=types[type], token=token)


@app.route("/geo/<string:token>/do", defaults={"type": "b"}, methods=["GET", "POST"])
# @app.route("/geo/<string:type>/<string:token>/do", methods=["GET", "POST"])
def locate(type, token):
    if type not in types or len(token) != 32:
        abort(404)
    form = forms[type]()
    if request.method == "GET":
        form.token.data = token
        return render_template("locate.html.jinja2", type=type, type_name=types[type], token=token,
                               form=form)
    elif form.validate_on_submit():
        resp, ok, message, detail = submit_form(form)
        return render_template("located.html.jinja2", type=type, token=token, message=message,
                               detail=detail, ok=ok, errors={})
    else:
        return render_template("located.html.jinja2", type=type, token=token,
                               message=gettext("Chyba."),
                               detail="", ok=False, errors=form.errors)


@app.errorhandler(404)
def error(error):
    return render_template("error.html.jinja2", message=str(error.code), detail=error.description)
