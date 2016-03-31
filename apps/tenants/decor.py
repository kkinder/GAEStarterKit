from functools import wraps
from flask import g, request, redirect, url_for, render_template


def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_account and g.current_account.tenant:
            return f(*args, **kwargs)
        elif g.current_account:
            return redirect(url_for('users.setup_tenant', next=request.url))
        else:
            return redirect(url_for('users.login', next=request.url))
    return decorated_function
