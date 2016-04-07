"""
Tools for authorization
"""
from functools import wraps

from flask import g, request, redirect, url_for, render_template, session
from flask.ext.babel import gettext

import config

_ = gettext


def account_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_account:
            return f(*args, **kwargs)
        else:
            session['post-auth-view'] = request.url_rule.endpoint
            return redirect(url_for('users.login', next=request.url))

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_account and g.current_account.is_superuser:
            return f(*args, **kwargs)
        elif not g.current_account:
            return redirect(url_for('users.login', next=request.url))
        else:
            return render_template('403.html'), 403

    return decorated_function


def redirect_to_next(default=config.default_view):
    if 'post-auth-view' in session:
        view = session['post-auth-view']
        del session['post-auth-view']
        return redirect(url_for(view))
    else:
        return redirect(url_for(default))
