"""
Provides generic object viewing functionality.
"""
import flask

from .GenericEditBase import GenericEditBase


class GenericRetrieve(GenericEditBase):
    template = 'generic-view.html'

    def post(self, urlsafe=None):
        return flask.abort(405)
