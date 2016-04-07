from google.appengine.ext import ndb

import datetime
import config
import flask
from flask import Flask
from flask import g

from markupsafe import Markup

from app import app
from security import login_manager, csrf
import i18n
from datahelper import put_later
import filters

##
## Debugging middleware for development
if config.DEVELOPMENT and config.enable_debug_panel:
    from werkzeug import debug

    try:
        app.wsgi_app = debug.DebuggedApplication(
            app.wsgi_app, evalex=True, pin_security=False,
        )
    except TypeError:
        app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, evalex=True)
    app.testing = False


for installed_app in config.install_apps:
    __import__(installed_app)
