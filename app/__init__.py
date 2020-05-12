from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object("config.Config")

from .home import home as home_blueprint
from .timeseries import timeseries as timeseries_blueprint


app.register_blueprint(home_blueprint)
app.register_blueprint(timeseries_blueprint)

csrf = CSRFProtect(app)
