from google.appengine.ext import ndb

import flask
from apps.admin.models import Activity
from apps.admin.register import admin_area
from apps.users import decor
from flask import Blueprint
from main import app
from .navigation import Menu

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/')
@decor.admin_required
def dashboard():
    return flask.render_template('dashboard.html',
                                 navbar=admin_area.navbar,
                                 recent_activity=Activity.query().order(-Activity.date_created))



#
# Maps model to admin view
app.register_blueprint(admin_blueprint, url_prefix='/admin/')
