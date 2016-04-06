"""
Just displays a simple "welcome" page for GAEStarterKit. You will most likely want to remove this from config.installed_apps and do your own thing.
"""
import config
from flask import Blueprint, render_template

blueprint = Blueprint('welcomekit', __name__, template_folder='templates')

@blueprint.route('/')
def welcome():
    return render_template('welcome.html')

from main import app

app.register_blueprint(blueprint)
