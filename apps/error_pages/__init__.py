"""
System-wide error pages. Override templates like 403.html, 404.html, and 405.html, etc.

If you must, you can change the content of these methods, but that's probably not necessary for most applications.
"""

from flask import render_template
from main import app


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def server_error(e):
    return render_template('405.html'), 405


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
