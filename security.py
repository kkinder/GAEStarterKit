from flask.ext.login import LoginManager, current_user
from flask.ext.seasurf import SeaSurf
from flask import session, g

from app import app

##
## Authentication middleware
login_manager = LoginManager()

@app.before_request
def before_request():
    """
    Inject current_account and current_tenant into template variables
    """
    if current_user.is_anonymous:
        g.current_account = None
        g.current_tenant = None
    else:
        g.current_account = current_user
        current_tenant = None
        if session.get('current_tenant'):
            current_tenant = Tenant.from_urlsafe(session['current_tenant'])
        g.current_tenant = current_tenant

    g.dirty_ndb = []

@login_manager.user_loader
def load_user(user_id):
    try:
        account = UserAccount.from_urlsafe(user_id)
    except:
        return None
    if account and account.is_enabled:
        return account

login_manager.init_app(app)

##
## CSRF security. We disable WTF_CSRF because we use SeaSurf instead.
app.config['WTF_CSRF_ENABLED'] = False
app.config['CSRF_COOKIE_NAME'] = 'csrf_token'
csrf = SeaSurf(app)


from apps.tenants.models import Tenant
from apps.users.models import UserAccount

