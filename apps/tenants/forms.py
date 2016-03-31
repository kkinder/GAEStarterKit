import wtforms
from util.SeaSurfForm import SeaSurfForm


class TenantSetupForm(SeaSurfForm):
    name = wtforms.StringField(validators=[wtforms.validators.DataRequired()])
