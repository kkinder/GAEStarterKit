"""
Provides a base class for wtforms usage throughout application. Integrates SeaCurf for CSRF protection, such that the csrf token is automatically included
in each form.
"""
from flask import g

from flask.ext.wtf import Form
from flask.ext.wtf.form import _Auto
from wtforms import HiddenField

from app import app

class SeaSurfForm(Form):
    def __init__(self, formdata=_Auto, obj=None, prefix='', csrf_context=None, secret_key=None, csrf_enabled=None, *args, **kwargs):
        super(SeaSurfForm, self).__init__(formdata, obj, prefix, csrf_context, secret_key, csrf_enabled, *args, **kwargs)

        csrf_name = app.config.get('CSRF_COOKIE_NAME', 'csrf_token')
        
        getattr(self, csrf_name).data = csrf._get_token()

    @staticmethod
    @app.before_request
    def add_csrf():
        csrf_name = app.config.get('CSRF_COOKIE_NAME', 'csrf_token')
        # token =
        #
        # if not token:
        #     raise ValueError('Expected CSRF token here')

        setattr(SeaSurfForm,
                csrf_name,
                HiddenField(default=''))

from security import csrf
