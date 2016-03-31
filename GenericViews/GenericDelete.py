"""
Provides generic deletion functionality.
"""

import time

import flask
from flask.ext.babel import lazy_gettext as _
from util import flasher

from .GenericEditBase import GenericEditBase


class GenericDelete(GenericEditBase):
    template = 'generic-delete.html'

    def post(self, urlsafe=None):
        if urlsafe:
            obj = self.fetch_object(urlsafe)
            obj.delete()
            time.sleep(.3)

            flasher.info(unicode(_('%(name)s deleted', name=self.name_singular)))
            return flask.redirect(flask.url_for(self.list_view))
        else:
            return flask.abort(404)
