"""
Provides generic editing of existing objects functionality.
"""
from flask.ext.babel import lazy_gettext as _

from util import flasher
from .GenericEditBase import GenericEditBase


class GenericEditExisting(GenericEditBase):
    def flash_message(self, obj):
        flasher.info(unicode(_('%(name)s updated', name=self.name_singular)))
