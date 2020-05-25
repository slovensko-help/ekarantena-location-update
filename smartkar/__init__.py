import os

import requests
from flask import Flask, render_template, request, abort
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, validators, FloatField

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["NCZI_TOKEN"] = os.environ.get("NCZI_TOKEN")

csrf = CSRFProtect(app)

try:
  os.makedirs(app.instance_path)
except OSError:
  pass


class LocationForm(FlaskForm):
  token = StringField("token", [validators.required(), validators.Length(min=32, max=32)])
  lat = FloatField("lat", [validators.required()])
  lng = FloatField("lng", [validators.required()])

@app.route("/geo/<string:token>", methods=["GET", "POST"])
def locate(token):
  if len(token) != 32:
    abort(404)

  form = LocationForm()
  if request.method == "GET":
    form.token.data = token
    return render_template("locate.html.jinja2", token=token, form=form)
  elif form.validate_on_submit():
    if app.env == "production":
      endpoint = "https://mojeezdravie.nczisk.sk/api/v1/sq/quarantine-geo-location"
    else:
      endpoint = "https://t.mojeezdravie.sk/api/v1/sq/quarantine-geo-location"
    data = {
      "vOneTimeToken": form.token.data,
      "nQuarantineAddressLatitude": form.lat.data,
      "nQuarantineAddressLongitude": form.lng.data
    }
    headers = {
      "Authorization": "Bearer " + app.config["NCZI_TOKEN"]
    }
    resp = requests.post(endpoint, json=data, headers=headers)
    ok = True
    message = ""
    if resp.status_code == 200:
      message = "Poloha domácej izolácie bola úspešne aktualizovaná."
    elif resp.status_code == 202:
      ok = False
      try:
        resp_data = resp.json()
        message = resp_data["ErrorText"]
      except Exception:
        message = "Chyba. Poloha domácej izolácie už bola raz aktualizovaná."
    elif resp.status_code == 400:
      ok = False
      message = "Chyba. Bad request."
    elif resp.status_code == 404:
      ok = False
      message = "Chyba. Nesprávny token."
    elif resp.status_code == 401:
      ok = False
      message = "Chyba. Unauthorized."
    elif resp.status_code == 403:
      ok = False
      message = "Chyba. Forbidden."
    return render_template("located.html.jinja2", lat=form.lat.data, lng=form.lng.data,
                           message=message, ok=ok)
  else:
    print(form.data)
