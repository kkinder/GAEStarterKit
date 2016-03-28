"""
Decorators and such we add to the universal app.
"""
import datetime

from flask import g

from main import app

@app.context_processor
def inject_user():
    """
    Adds user and auth information to flask templates
    """
    return dict(
        current_account=g.current_account,
        current_auth=g.current_auth,
    )
