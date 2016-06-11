"""
Contains base class for ndb models. This adds functionality that is expected (or at least useful) elsewhere in GEAStarterKit.
"""
import random
import string

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext.ndb.polymodel import PolyModel

from NdbSearchableBase import SearchableModel

alphabet = string.digits + string.letters


class BaseModel(SearchableModel, ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True, required=True)
    date_modified = ndb.DateTimeProperty(auto_now=True, required=True)

    def to_dict(self, include=None, exclude=None):
        data = super(BaseModel, self).to_dict(include=include, exclude=exclude)
        if (include and 'urlsafe' in include) or (exclude and 'urlsafe' not in exclude) or not (exclude or include):
            data['urlsafe'] = self.key.urlsafe()
        return data

    def get_class_badge(self):
        if hasattr(self, 'class_'):
            return self.class_[-1]
        else:
            return self.__class__.__name__

    def delete(self):
        self.key.delete()

    @classmethod
    def _generate_token(cls, length=20):
        r = random.SystemRandom()
        return ''.join(r.choice(alphabet) for _ in range(length))

