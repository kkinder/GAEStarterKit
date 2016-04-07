"""
Adds useful stuff to render and deal with forms.
"""
from markupsafe import Markup
import wtforms

from app import app

def render_field(field, *args, **kwargs):
    #
    # Add any flags
    for v in field.validators:
        if isinstance(v, wtforms.validators.DataRequired):
            kwargs['required'] = ''
        elif isinstance(v, wtforms.validators.Email):
            kwargs['type'] = 'email'
        elif isinstance(v, wtforms.validators.EqualTo):
            kwargs['data-parsley-equalto'] = '#{}'.format(v.fieldname)

        if v.message:
            kwargs['data-parsley-error-message'] = v.message


    kwargs['data-parsley-errors-container'] = '#errors-{}'.format(field.id)
    return field(*args, **kwargs) #+ Markup('<div id="errors-{}"></div>'.format(field.id))

app.jinja_env.globals.update(render_field=render_field)

