"""
Provides the base view for other Generic views. It is unlikely that you will use this. Refer to this class, however, on overriding functionality of
generic views for your application.
"""

import time

import flask
from flask.views import MethodView

from . import _from_camel


class GenericBase(MethodView):
    model = None
    template = None
    base_template = "base.html"

    variable_current_object = 'current_object'
    variable_rows = 'rows'
    variable_next_cursor = 'next_cursor'
    variable_last_cursor = 'last_cursor'

    variable_form = 'form'

    name_singular = None
    name_plural = None

    retrieve_view = None
    edit_view = None
    new_view = None
    list_view = None
    delete_view = None

    form_exclude = ['class']  # Exclude these when editing/viewing fields.
    list_fields = None        # Include these when listing entities.
    wtforms_field_args = None # Field args to pass to wtform_appengine model_form

    page_size = 25

    not_found_template = '404.html'
    permission_denied_template = '403.html'
    sleep_on_not_found = .25  # To slow down brute-force URL guessing schemes, sleep this many seconds each time a 404 is generated.

    extra_context = {}

    def __init__(self):
        super(GenericBase, self).__init__()

        if not self.name_singular:

            self.name_singular = _from_camel(self.model._class_name())

        if not self.name_plural:
            if self.name_singular.endswith('s'):
                self.name_plural = '%ses' % self.name_singular
            else:
                self.name_plural = '%ss' % self.name_singular

    def get_retrieve_url(self, object):
        if self.retrieve_view:
            return flask.url_for(self.retrieve_view, urlsafe=object.key.urlsafe())
        else:
            return None

    def get_edit_url(self, object):
        if self.edit_view:
            return flask.url_for(self.edit_view, urlsafe=object.key.urlsafe())
        else:
            return None

    def add_extra_fields(self, obj):
        obj._retrieve_url = self.get_retrieve_url(obj)
        obj._edit_url = self.get_edit_url(obj)

        for field, prop in obj._properties.items():
            if getattr(prop, '_auto_now_add', False):
                obj._created = getattr(obj, field)
            if getattr(prop, '_auto_now', False):
                obj._modified = getattr(obj, field)
        return obj

    def user_has_access(self, object):
        """
        Override to determine whether user has access to a particular object.
        """
        return True

    def show_403(self):
        return flask.render_template(self.permission_denied_template), 403

    def show_404(self):
        if self.sleep_on_not_found:
            time.sleep(self.sleep_on_not_found)
        return flask.render_template(self.not_found_template), 404

    def get_context(self):
        context = self.extra_context

        context.update(dict(
            model=self.model,
            name_singular=self.name_singular,
            name_plural=self.name_plural,
            retrieve_view=self.retrieve_view,
            new_view=self.new_view,
            list_view=self.list_view,
            edit_view=self.edit_view,
            delete_view=self.delete_view,
            page_size=self.page_size,
            base_template=self.base_template,
            list_fields=self.list_fields
        ))

        return context

    def render(self, **extra_context):
        context = self.get_context()
        context.update(extra_context)
        return flask.render_template(self.template, **context)
