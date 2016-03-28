"""
Just a handy way of remembering what the categories are you can use for flask.flash.
"""

import flask


def info(message):
    flask.flash(message, 'info')


def success(message):
    flask.flash(message, 'success')


def warning(message):
    flask.flash(message, 'warning')


def error(message):
    flask.flash(message, 'danger')

