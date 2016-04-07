"""
System-wide error pages. Override templates like 403.html, 404.html, and 405.html, etc.

If you must, you can change the content of these methods, but that's probably not necessary for most applications.
"""

from flask import render_template
from app import app


@app.errorhandler(401)
def not_authorized(e):
    return render_template('401.html'), 403


@app.errorhandler(403)
def permission_denied(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
