from google.appengine.ext import ndb

import config
import flask
from flask import Flask
from flask import g
from flask.ext.babel import Babel
from flask.ext.login import LoginManager, current_user
from flask.ext.seasurf import SeaSurf
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = config.SECRET_STRING
app.production = False
app.debug = app.development = True

##
## Authentication middleware
login_manager = LoginManager()

@app.before_request
def before_request():
    if current_user.is_anonymous:
        g.current_account = None
    else:
        g.current_account = current_user
    g.dirty_ndb = []

@login_manager.user_loader
def load_user(user_id):
    try:
        account = UserAccount.from_urlsafe(user_id)
    except:
        return None
    if account.is_enabled:
        return account

login_manager.init_app(app)


##
## Internationalization
import datetime

babel = Babel(app)
@babel.localeselector
def get_locale():
    return flask.request.accept_languages.best_match(config.languages.keys())

from flask_moment import Moment
moment = Moment(app)

@app.context_processor
def inject_locale():
    return dict(
        global_now=datetime.datetime.utcnow(),
        js_dateformat='YYYY-MM-DD',
        js_timeformat='HH:MM:SS',
        js_datetimeformat='YYYY-MM-DD HH:MM:SS'
    )


##
## CSRF Security
app.config['WTF_CSRF_ENABLED'] = False
app.config['CSRF_COOKIE_NAME'] = 'csrf_token'
csrf = SeaSurf(app)


##
## NDB tweaks for putting all objects from a request at once.
def put_later(*objs):
    for obj in objs:
        if obj not in g.dirty_ndb:
            g.dirty_ndb.append(obj)

@app.after_request
def store_ndb(response):
    try:
        if g.dirty_ndb:
            ndb.put_multi(g.dirty_ndb)
            g.dirty_ndb = []
    finally:
        return response


##
## Utilties for dealing with forms
import util.form_util
util.form_util.init(app)

##
## Just sometimes helpful for debug/devel
@app.template_filter('dump')
def reverse_filter(s):
    markup = '<table>'
    single_underscores = []
    double_underscores = []
    main_vars = []

    for k in dir(s):
        try:
            v = repr(getattr(s, k))
        except Exception as e:
            v = 'Error Fetching Atribute: %r' % (e,)
        if k.startswith('__'):
            double_underscores.append((k, v))
        elif k.startswith('_'):
            single_underscores.append((k, v))
        else:
            main_vars.append((k, v))

    main_vars.extend(single_underscores)
    #main_vars.extend(double_underscores)

    return Markup(flask.render_template('_dump.html', items=main_vars))


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


from apps.users.models import UserAccount

for installed_app in config.install_apps:
    __import__(installed_app)
