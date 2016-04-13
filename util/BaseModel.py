"""
Contains base class for ndb models. This adds functionality that is expected (or at least useful) elsewhere in GEAStarterKit.
"""
import random
import string

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext.ndb.polymodel import PolyModel

GENERAL_INDEX = 'general-index'

SEARCHABLE_PROPERTY_TYPES = {
    ndb.TextProperty: search.TextField,
    ndb.IntegerProperty: search.NumberField,
    ndb.FloatProperty: search.NumberField,
    ndb.DateProperty: search.DateField
}

alphabet = string.digits + string.letters


class BaseModel(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True, required=True)
    date_modified = ndb.DateTimeProperty(auto_now=True, required=True)

    searching_enabled = True
    searchable_fields = None # defaults to all fields

    def get_class_badge(self):
        if hasattr(self, 'class_'):
            return self.class_[-1]
        else:
            return self.__class__.__name__

    @classmethod
    def from_urlsafe(cls, urlsafe):
        try:
            key = ndb.Key(urlsafe=urlsafe)
        except:
            return None
        obj = key.get()
        if obj and isinstance(obj, cls):
            return obj

    def delete(self):
        self.key.delete()

    def search_get_index(self):
        return search.Index(name=GENERAL_INDEX)

    def search_get_document_id(self):
        return self.key.urlsafe()

    def search_update_index(self):
        doc_id = doc_id=self.search_get_document_id()

        fields = []

        if hasattr(self, '_class_key'):
            facets = []
            for class_name in self._class_key():
                fields.append(search.AtomField('class_name', class_name))
        else:
            fields = [search.AtomField('class_name', self.__class__.__name__)]

        index = self.search_get_index()

        if self.searchable_fields is None:
            searchable_fields = []

            for field, prop in self._properties.items():
                if field == 'class':
                    continue
                for class_, field_type in SEARCHABLE_PROPERTY_TYPES.items():
                    if isinstance(prop, class_):
                        searchable_fields.append(field)
        else:
            searchable_fields = self.searchable_fields


        for f in set(searchable_fields):
            prop = self._properties[f]
            value = getattr(self, f)
            field = None
            field_found = False
            for class_, field_type in SEARCHABLE_PROPERTY_TYPES.items():
                if isinstance(prop, class_):
                    field_found = True
                    if value is not None:
                        if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
                            for v in value:
                                field = field_type(name=f, value=v)
                        else:
                            field = field_type(name=f, value=value)
            if not field_found:
                raise ValueError('Cannot find field type for %r on %r' % (prop, self.__class__))

            if field is not None:
                fields.append(field)

        document = search.Document(doc_id, fields=fields)
        index.put(document)

    @classmethod
    def get_from_search_doc(cls, doc_id):
        # Sometimes passing a document itself is handy.
        if hasattr(doc_id, 'doc_id'):
            doc_id = doc_id.doc_id
        return cls.from_urlsafe(doc_id)

    def _post_put_hook(self, future):
        if self.searching_enabled:
            self.search_update_index()

        return super(BaseModel, self)._post_put_hook(future)

    @classmethod
    def _generate_token(cls, length=20):
        r = random.SystemRandom()
        return ''.join(r.choice(alphabet) for _ in range(length))

