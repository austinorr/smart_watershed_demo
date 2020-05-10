from flask import Blueprint

timeseries = Blueprint('timeseries', __name__)

from . import views
