"""
Contains template filters we add for extra usefulness.

Note that this isn't necessarily an exhaustive list of all filters apps or other utilities could add.
"""
from flask import render_template
from markupsafe import Markup

from app import app
import util.form_util

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

    return Markup(render_template('_dump.html', items=main_vars))

