"""
Tools for authorization
"""

from functools import wraps
from flask import g, request, redirect, url_for, render_template


def account_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_account:
            return f(*args, **kwargs)
        else:
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
