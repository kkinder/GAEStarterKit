"""
Provides generic object creation functionality.
"""

from flask.ext.babel import lazy_gettext as _

from util import flasher
from .GenericEditBase import GenericEditBase


class GenericEditNew(GenericEditBase):
    def flash_message(self, obj):
        flasher.info(unicode(_('New %(name)s created', name=self.name_singular)))
