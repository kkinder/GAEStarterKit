"""
Login-related pages. Includes password reset, etc.
"""

import logging
import time

import flask
from google.appengine.api import users
from flask import render_template, request, make_response, g
from flask.ext.babel import gettext
from flask.ext.login import login_user, logout_user, login_required

import config
from GenericViews.GenericEditExisting import GenericEditExisting
from apps.admin.models import Activity
from apps.users import blueprint
from apps.users.decor import account_required
from apps.users.forms import EmailSignupForm, TenantSetupForm, EmailLoginForm, PasswordRecoveryForm, PasswordResetForm
from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter
from main import app, put_later
from util import flasher
import models

_ = gettext

# Instantiate Authomatic.
authomatic = Authomatic(config.AUTHOMATIC_CONFIG, config.SECRET_STRING)


@blueprint.route('/login/', defaults={'provider_code': None}, methods=['GET', 'POST'])
@blueprint.route('/login/<provider_code>/', methods=['GET', 'POST'])
def login(provider_code):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    next = flask.request.args.get('next', flask.url_for('users.login', provider_code=provider_code))

    if not provider_code:
        form = EmailLoginForm(request.form)
        if request.method == 'POST' and form.validate():
            email = form.email.data
            auth = models.EmailAuth.from_email(email, create=False)
            if auth and auth.check_password(form.password.data):
                return _login_user(auth, None)
            else:
                time.sleep(config.security_wait)
                flasher.warning(_('Invalid email address or password'))

        return render_template('login.html', login_providers=config.AUTHOMATIC_CONFIG, next=next, form=form)

    if provider_code == 'google':
        if users.get_current_user():
            user_account, auth = models.UserAccount.from_google(users.get_current_user(), is_superuser=users.is_current_user_admin())
            return _login_user(auth, next)
        else:
            return flask.redirect(users.create_login_url(dest_url=flask.request.url))

    response = make_response()
    result = authomatic.login(WerkzeugAdapter(request, response), provider_code)

    logging.info('Authomatic result for %r: %r. Response is %r', provider_code, result, response)

    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.error:
            flasher.error(result.error)
            return flask.redirect(flask.url_for('users.login'))

        if result.user:
            # We need to update the user to get more info.
            result.user.update()

        user_account, auth = models.UserAccount.from_authomatic(result.user, provider_code=provider_code)
        return _login_user(auth, next, result=result)
    return response


def _login_user(auth, next, flash_message=True, **template_args):
    login_user(auth)
    if flash_message:
        flasher.success(_('You are now logged in'))
    if next and 0:
        return flask.redirect(next)
    else:
        return flask.redirect('/')


@blueprint.route("/logout/")
@login_required
def logout():
    next_url = '/'

    if g.current_auth and g.current_auth.auth_type == 'google':
        logout_user()
        return flask.redirect(users.create_logout_url(next_url))
    else:
        logout_user()
        return flask.redirect(next_url)


@blueprint.route('/signup/email/', methods=['GET', 'POST'])
def signup_email():
    form = EmailSignupForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        auth = models.EmailAuth.from_email(email, create=False)
        if auth:
            # Account exists. Check password.
            assert isinstance(auth, models.EmailAuth)
            if auth.check_password(form.password.data):
                return _login_user(auth, None)
            else:
                flasher.warning(_('A user with that email address already exists'))
                return flask.redirect(flask.url_for('users.login'))
        else:
            account, auth = models.UserAccount.from_email(form.email.data)
            auth.set_password(form.password.data)
            auth.put()
            flasher.info(_('Thanks for signing up'))
            return _login_user(auth, None, flash_message=False)
    return render_template('signup_email.html', form=form)


@blueprint.route('/setup/', methods=['GET', 'POST'])
@account_required
def setup_tenant():
    form = TenantSetupForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        tenant = models.Tenant(name=name, owner=g.current_account.key)
        tenant.put()
        activity = Activity(user=g.current_account.key, subject=tenant.key, type='tenant', tags=['new-tenant'])

        g.current_account.tenant = tenant.key
        g.current_account.put()

        put_later(g.current_account, activity)

        flasher.info(_('Account Created'))
        return flask.redirect('/')
    return render_template('setup_tenant.html', form=form)


@blueprint.route('/verify/<auth_id>/<token>/')
def verify(auth_id, token):
    key = models.ndb.Key(urlsafe=auth_id)

    auth = key.get()
    if not isinstance(auth, models.EmailAuth):
        time.sleep(config.security_wait)
        return render_template('no_token.html'), 404

    if auth.verify_email(token=token):
        login_user(auth)
        return render_template('verified.html')
    else:
        time.sleep(config.security_wait)
        return render_template('no_token.html'), 404


@blueprint.route('/reset-password/<auth_id>/<token>/', methods=['GET', 'POST'])
def reset_password(auth_id, token):
    k = models.ndb.Key(urlsafe=auth_id)
    auth = k.get()

    if not isinstance(auth, models.EmailAuth):
        time.sleep(config.security_wait)
        return render_template('password-reset-not-found.html'), 404

    if auth.verify_reset_password(token=token):
        form = PasswordResetForm(request.form)
        if request.method == 'POST' and form.validate():
            password = form.password.data
            auth.set_password(password)
            auth.put()
            flasher.info(_("Password reset. You may now login."))
            return flask.redirect(flask.url_for('users.login'))

        return render_template('password-reset.html', form=form)
    else:
        time.sleep(config.security_wait)
        return render_template('password-reset-not-found.html'), 404


@blueprint.route('/forgot-password/', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordRecoveryForm(request.form)
    message = None
    if request.method == 'POST' and form.validate():
        email = form.email.data
        auth = models.EmailAuth.from_email(email, create=False)
        if auth:
            auth.recover_password()

        flasher.info(_(
            'If an account exists with that email address, a verification email will be sent. If no account exists with that address, no email will be sent.'))
    return render_template('forgot-password.html', form=form, message=message)


class EditMyProfile(GenericEditExisting):
    model = models.UserAccount
    template = 'profile.html'

    decorators = [login_required]
    form_exclude = ['is_superuser', 'primary_auth', 'tenant']

    def handle_url(self, FormClass, urlsafe=None):
        obj = g.current_account
        form = FormClass(flask.request.form, obj)
        is_new = False

        return form, is_new, obj

    def flash_message(self, obj):
        flasher.info(unicode(_('Profile Saved')))

    def redirect_after_completion(self):
        return flask.redirect(flask.url_for('users.profile'))



# @blueprint.route('/profile/')
# @login_required
# def profile():
#     return render_template('profile.html')

blueprint.add_url_rule('/profile/', view_func=EditMyProfile.as_view('profile'))

from apps.admin.register import quickstart_admin_model

quickstart_admin_model(models.UserAccount, 'accounts', 'accounts', 'Users', enable_new=False, list_fields=['authentication_methods'])
quickstart_admin_model(models.UserAuth, 'auths', 'auths', 'Users', enable_new=False)
quickstart_admin_model(models.Tenant, 'tenants', 'tenants', 'Users')
