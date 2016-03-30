"""
Just a handy way of remembering what the categories are you can use for flask.flash.
"""

import flask


def info(message):
    flask.flash(unicode(message), 'info')


def success(message):
    flask.flash(unicode(message), 'success')


def warning(message):
    flask.flash(unicode(message), 'warning')


def error(message):
    flask.flash(unicode(message), 'danger')

