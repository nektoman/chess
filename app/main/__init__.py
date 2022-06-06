from flask import Blueprint

rooms={}

main = Blueprint('main', __name__)

from . import routes, events
