import os

from flask import Flask, render_template, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, validators, FloatField

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

csrf = CSRFProtect(app)

try:
  os.makedirs(app.instance_path)
except OSError:
  pass

class LocationForm(FlaskForm):
  token = StringField("token", [validators.required(), validators.Length(min=64,max=64)])
  lat = FloatField("lat", [validators.required()])
  lng = FloatField("lng", [validators.required()])
  alt = FloatField("alt", [validators.required()])
  accuracy = FloatField("accuracy", [validators.required()])


@app.route("/")
def index():
  return render_template("index.html.jinja2")


@app.route("/<string:token>", methods=["GET", "POST"])
def locate(token):
  form = LocationForm()
  if request.method == "GET":
    return render_template("locate.html.jinja2", token=token, form=form)
  elif form.validate_on_submit():
    pass

