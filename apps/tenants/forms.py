import wtforms
from apps.tenants.models import TenantMembership
from flask.ext.babel import lazy_gettext as _
from util.SeaSurfForm import SeaSurfForm


class TenantSetupForm(SeaSurfForm):
    name = wtforms.StringField(validators=[wtforms.validators.DataRequired()])


class InviteMemberForm(SeaSurfForm):
    email = wtforms.StringField(validators=[wtforms.validators.email(), wtforms.validators.DataRequired()])
    user_type = wtforms.SelectField("User Access Level", default=TenantMembership.PRIVILEGE_USER, choices=TenantMembership.USER_TYPE_CHOICES,
                                    validators=[wtforms.validators.DataRequired()])


class ChoosePasswordForm(SeaSurfForm):
    password = wtforms.PasswordField(_('Password'), [
        wtforms.validators.DataRequired()
    ])
    confirm = wtforms.PasswordField(_('Repeat Password'), [
        wtforms.validators.EqualTo('password', message=_('Passwords must match'))
    ])
