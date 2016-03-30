"""
Provides a full CRUD template, all inclusive. Very basic example is as follows.

    class Widget(BaseModel):
        name = ndb.StringProperty()

        def __unicode__(self):
            return self.name or '<Untitled Widget>'


    class WidgetBlueprint(GenericCrud):
        model = Widget


    blueprint = WidgetBlueprint('widgets', 'widgets')

    app.register_blueprint(blueprint, url_prefix='/widgets')

It's that easy.
"""

from flask import Blueprint

from GenericViews.GenericRetrieve import GenericRetrieve
from GenericViews.GenericList import GenericList
from GenericViews.GenericEditNew import GenericEditNew
from GenericViews.GenericEditExisting import GenericEditExisting
from GenericViews.GenericDelete import GenericDelete


class GenericCrud(Blueprint):
    model = None
    base_template = "base.html"

    variable_current_object = 'current_object'
    variable_rows = 'rows'
    variable_next_cursor = 'next_cursor'
    variable_last_cursor = 'last_cursor'

    variable_form = 'form'

    name_singular = None
    name_plural = None

    form_exclude = ['class']   # Exclude these when editing/viewing fields.
    form_include = None        # IF specified, only show these fields
    list_fields = None         # Include these when listing entities.
    wtforms_field_args = None  # Field args to pass to wtform_appengine model_form

    page_size = 25

    not_found_template = '404.html'
    permission_denied_template = '403.html'
    sleep_on_not_found = .25  # To slow down brute-force URL guessing schemes, sleep this many seconds each time a 404 is generated.

    extra_context = {}  # Extra variables passed to complates

    decorators = []

    enable_list = True
    enable_retrieve = True
    enable_delete = True
    enable_edit = True
    enable_new = True

    def __init__(self, name, import_name, static_folder=None, static_url_path=None, template_folder='GenericViews/templates', url_prefix=None, subdomain=None,
                 url_defaults=None):
        super(GenericCrud, self).__init__(name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults)

        view_names = {}
        for view_type in ('list', 'retrieve', 'delete', 'edit', 'new'):
            if getattr(self, 'enable_%s' % view_type):
                view_names[view_type] = '%s.%s' % (name, view_type)
                if view_type == 'list':
                    view_names['list_cursor'] = '%s.list_cursor' % name
            else:
                view_names[view_type] = None
                if view_type == 'list':
                    view_names['list_cursor'] = None

        class GenericConfig(object):
            model = self.model
            base_template = self.base_template

            variable_current_object = self.variable_current_object
            variable_rows = self.variable_rows
            variable_next_cursor = self.variable_next_cursor
            variable_last_cursor = self.variable_last_cursor

            variable_form = self.variable_form

            name_singular = self.name_singular
            name_plural = self.name_plural

            form_exclude = self.form_exclude
            fomr_include = self.form_include
            list_fields = self.list_fields
            wtforms_field_args = self.wtforms_field_args

            page_size = self.page_size

            not_found_template = self.not_found_template
            permission_denied_template = self.permission_denied_template
            sleep_on_not_found = self.sleep_on_not_found

            extra_context = self.extra_context

            decorators = self.decorators

            retrieve_view = view_names['retrieve']
            new_view = view_names['new']
            list_view = view_names['list']
            list_view_cursor = view_names['list_cursor']
            delete_view = view_names['delete']
            edit_view = view_names['edit']

        if self.enable_list:
            class List(GenericConfig, GenericList):
                pass

            self.add_url_rule('/', view_func=List.as_view('list'))

        if self.enable_retrieve:
            class Retrieve(GenericConfig, GenericRetrieve):
                pass

            self.add_url_rule('/<urlsafe>/', view_func=Retrieve.as_view('retrieve'))

        if self.enable_new:
            class New(GenericConfig, GenericEditNew):
                pass

            self.add_url_rule('/new/', view_func=New.as_view('new'))

        if self.enable_edit:
            class Edit(GenericConfig, GenericEditExisting):
                pass

            self.add_url_rule('/<urlsafe>/edit/', view_func=Edit.as_view('edit'))

        if self.enable_delete:
            class Delete(GenericConfig, GenericDelete):
                pass

            self.add_url_rule('/<urlsafe>/delete/', view_func=Delete.as_view('delete'))
