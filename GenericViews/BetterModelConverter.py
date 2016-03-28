"""
Extends wtforms_appengine to use html5 components from wtforms_components
"""
from wtforms import TextAreaField
from wtforms_appengine.ndb import ModelConverter
from wtforms_components import DateTimeField, DateField, TimeField


class MarkdownField(TextAreaField):
    """
    Used in uikit templates to render a markdown editor.
    """
    pass


class BetterModelConverter(ModelConverter):
    def fallback_converter(self, model, prop, kwargs):
        raise NotImplementedError, u'No converter for %s.%r [%r]' % (model.__class__.__name__, prop, kwargs)

    def convert_MarkdownProperty(self, model, prop, kwargs):
        return MarkdownField(**kwargs)

    def convert_DateTimeProperty(self, model, prop, kwargs):
        """Returns a form field for a ``ndb.DateTimeProperty``."""
        if prop._auto_now or prop._auto_now_add:
            return None

        return DateTimeField(format='%Y-%m-%d %H:%M', **kwargs)

    def convert_DateProperty(self, model, prop, kwargs):
        """Returns a form field for a ``ndb.DateProperty``."""
        if prop._auto_now or prop._auto_now_add:
            return None

        return DateField(format='%Y-%m-%d', **kwargs)

    def convert_TimeProperty(self, model, prop, kwargs):
        """Returns a form field for a ``ndb.TimeProperty``."""
        if prop._auto_now or prop._auto_now_add:
            return None

        return TimeField(format='%H:%M', **kwargs)
