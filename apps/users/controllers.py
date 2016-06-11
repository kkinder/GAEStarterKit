"""
Login-related pages. Includes password reset, etc.
"""

import logging
import time

from google.appengine.api import users
import flask
from flask import render_template, request, make_response, g
from flask.ext.babel import gettext
from flask.ext.login import login_user, logout_user, login_required

import config
from GenericViews.GenericEditExisting import GenericEditExisting
from apps.users import blueprint
from apps.users.decor import account_required, redirect_to_next
from apps.users.forms import EmailSignupForm, EmailLoginForm, PasswordRecoveryForm, PasswordResetForm, AddEmailForm
from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter
from datahelper import put_later
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
    if not provider_code:
        form = EmailLoginForm(request.form)
        if request.method == 'POST' and form.validate():
            email = form.email.data
            auth = models.EmailAuth.from_email(
                email,
                create=False,
                current_account=g.current_account)
            if auth:
                user_account = auth.user_account.get()
                if user_account.check_password(form.password.data):
                    return _login_user(user_account)
                else:
                    time.sleep(config.security_wait)
                    flasher.warning(_('Invalid email address or password'))
            else:
                time.sleep(config.security_wait)
                flasher.warning(_('Invalid email address or password'))

        return render_template('login.html', login_providers=config.AUTHOMATIC_CONFIG, form=form)

    elif provider_code == 'google':
        if users.get_current_user():
            user_account, auth = models.UserAccount.from_google(
                users.get_current_user(),
                is_superuser=users.is_current_user_admin(),
                current_account=g.current_account)
            return _login_user(user_account)
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

        user_account, auth = models.UserAccount.from_authomatic(
            result.user,
            provider_code=provider_code,
            current_account=g.current_account)
        return _login_user(user_account, result=result)
    return response


def _login_user(user_account, flash_message=True, **template_args):
    assert isinstance(user_account, models.UserAccount)

    login_user(user_account)
    if flash_message:
        flasher.success(_('You are now logged in'))

    return redirect_to_next()


@blueprint.route("/logout/")
@login_required
def logout():
    if users.get_current_user():
        return flask.redirect(users.create_logout_url(flask.url_for('users.logout')))

    for key in ('current_tenant', 'current_account'):
        if key in flask.session:
            del flask.session[key]

    logout_user()
    return flask.render_template('loggedout.html')


@blueprint.route('/signup/email/', methods=['GET', 'POST'])
def signup_email():
    form = EmailSignupForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        auth = models.EmailAuth.from_email(email, create=False)
        if auth:
            # Account exists. Check password.
            assert isinstance(auth, models.EmailAuth)
            account = auth.user_account.get()

            if account.check_password(form.password.data):
                return _login_user(account)
            else:
                flasher.warning(_('A user with that email address already exists'))
                return flask.redirect(flask.url_for('users.login'))
        else:
            account, auth = models.UserAccount.from_email(form.email.data, current_account=g.current_account)
            account.set_password(form.password.data)
            models.ndb.put_multi((account, auth))
            flasher.info(_('Thanks for signing up'))
            return _login_user(account, flash_message=False)
    return render_template('signup_email.html', form=form)


@blueprint.route('/verify/<auth_id>/<token>/')
def verify(auth_id, token):
    key = models.ndb.Key(urlsafe=auth_id)

    auth = key.get()
    if not isinstance(auth, models.EmailAuth):
        time.sleep(config.security_wait)
        return render_template('no_token.html'), 404

    if auth.verify_email(token=token):
        login_user(auth.user_account.get())
        return render_template('verified.html')
    else:
        time.sleep(config.security_wait)
        return render_template('no_token.html'), 404


@blueprint.route('/reset-password/<auth_id>/<token>/', methods=['GET', 'POST'])
def reset_password(auth_id, token):
    auth = models.EmailAuth.from_urlsafe(auth_id)
    if not auth:
        time.sleep(config.security_wait)
        return render_template('password-reset-not-found.html'), 404
    assert isinstance(auth, models.EmailAuth)

    account = auth.user_account.get()
    assert isinstance(account, models.UserAccount)

    if not isinstance(auth, models.EmailAuth):
        time.sleep(config.security_wait)
        return render_template('password-reset-not-found.html'), 404

    if account.verify_reset_password(token=token):
        form = PasswordResetForm(request.form)
        if request.method == 'POST' and form.validate():
            password = form.password.data

            account.set_password(password)
            account.put()
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
            account = auth.user_account.get()
            account.recover_password()

        flasher.info(_(
            'If an account exists with that email address, a verification email will be sent. If no account exists with that address, no email will be sent.'))
    return render_template('forgot-password.html', form=form, message=message)


@blueprint.route('/profile/ajax/<auth>/resend-verification-email/', methods=['POST'])
def ajax_resend_verification_email(auth):
    auth = models.EmailAuth.from_urlsafe(auth)
    if auth and auth.user_account == g.current_account.key:
        auth.send_verification_email()
        return flask.jsonify({'email_sent': auth.key.id()})
    else:
        return flask.abort(404)


@blueprint.route('/profile/ajax/<auth>/make-primary/', methods=['POST'])
def ajax_make_primary_email(auth):
    auth = models.UserAuth.from_urlsafe(auth)
    if auth and auth.user_account == g.current_account.key:
        auth.set_primary()
        time.sleep(.5)  # Let any caches catch a breather
        return flask.jsonify({'primary': auth.key.id()})
    else:
        return flask.abort(404)


@blueprint.route('/profile/ajax/<auth>/remove/', methods=['POST'])
def ajax_remove_auth(auth):
    auth = models.UserAuth.from_urlsafe(auth)
    if auth and auth.user_account == g.current_account.key:
        if auth.is_primary:
            return flask.abort(403)
        else:
            old_id = auth.key.id()
            auth.delete()
            time.sleep(.5)
            return flask.jsonify({'removed': old_id})
    else:
        return flask.abort(404)


class EditMyProfile(GenericEditExisting):
    model = models.UserAccount
    template = 'profile.html'

    decorators = [account_required]
    form_include = ['name']

    def post(self, urlsafe=None):
        if flask.request.form.get('action', '') == 'add-email':
            return self.handle_add_email()
        else:
            return super(EditMyProfile, self).post(urlsafe)

    def get_context(self):
        context = super(EditMyProfile, self).get_context()
        context['add_email_form'] = AddEmailForm()
        return context

    def handle_url(self, FormClass, urlsafe=None):
        obj = g.current_account
        form = FormClass(flask.request.form, obj)
        is_new = False

        return form, is_new, obj

    def flash_message(self, obj):
        flasher.info(_('Profile Saved'))

    def redirect_after_completion(self):
        return flask.redirect(flask.url_for('users.profile'))

    def handle_add_email(self):
        form = AddEmailForm(flask.request.form)

        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            existing_auth = models.EmailAuth.get_by_id(email)

            if existing_auth:
                flasher.error(_('Another user is already using this email address.'))

            else:
                flasher.info(_('Email address verification sent.'))
                new_auth = models.EmailAuth.from_email(form.email.data, create=True, email_is_verified=False)
                new_auth.user_account = g.current_account.key
                put_later(new_auth)

        else:
            flasher.error(_(' '.join(form.errors.values())))
        return flask.redirect(flask.url_for('users.profile'))


blueprint.add_url_rule('/profile/', view_func=EditMyProfile.as_view('profile'))

from apps.admin.register import quickstart_admin_model

quickstart_admin_model(models.UserAccount, menu_section='Users', enable_new=False, list_fields=['authentication_methods'])
quickstart_admin_model(models.UserAuth, menu_section='Users', enable_new=False)
