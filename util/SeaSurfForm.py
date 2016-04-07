"""
Provides a base class for wtforms usage throughout application. Integrates SeaCurf for CSRF protection, such that the csrf token is automatically included
in each form.
"""
from flask.ext.wtf import Form
from wtforms import HiddenField

from app import app

class SeaSurfForm(Form):
    @staticmethod
    @app.before_request
    def add_csrf():
        csrf_name = app.config.get('CSRF_COOKIE_NAME', 'csrf_token')
        token = csrf._get_token()

        setattr(SeaSurfForm,
                csrf_name,
                HiddenField(default=token))

from security import csrf
