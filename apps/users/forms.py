import wtforms
from flask.ext.babel import lazy_gettext as _
from util.SeaSurfForm import SeaSurfForm


class EmailSignupForm(SeaSurfForm):
    email = wtforms.StringField(validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
    password = wtforms.PasswordField(_('Password'), [
        wtforms.validators.DataRequired()
    ])
    confirm = wtforms.PasswordField(_('Repeat Password'), [
        wtforms.validators.EqualTo('password', message='Passwords must match')
    ])
    accept_tos = wtforms.BooleanField(_('I accept the TOS'), [wtforms.validators.DataRequired(message=_('You must accept the Terms of Service to continue'))])


class EmailLoginForm(SeaSurfForm):
    email = wtforms.StringField(validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
    password = wtforms.PasswordField(_('Password'), [wtforms.validators.DataRequired()])


class PasswordRecoveryForm(SeaSurfForm):
    email = wtforms.StringField(validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])


class PasswordResetForm(SeaSurfForm):
    password = wtforms.PasswordField(_('Password'), [
        wtforms.validators.DataRequired()
    ])
    confirm = wtforms.PasswordField(_('Repeat Password'), [
        wtforms.validators.EqualTo('password', message=_('Passwords must match'))
    ])


class TenantSetupForm(SeaSurfForm):
    name = wtforms.StringField(validators=[wtforms.validators.DataRequired()])


class AddEmailForm(SeaSurfForm):
    action = wtforms.HiddenField(default='add-email')
    email = wtforms.StringField(validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
