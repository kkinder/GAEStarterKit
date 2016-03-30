from google.appengine.ext import ndb
import flask

from apps.users.decor import admin_required
from apps.admin import navbar
from GenericViews.GenericCrud import GenericCrud
from .controllers import admin_views
from main import app


def get_object_view(object):
    """
    Returns the admin/CRUD view for a particular object, if there is one. The object can be an ndb object, or an ndb key. It assumes the view accepts
    urlsafe (from the key) as a parameter.

    :param object: NDB object or NDB key.
    :return: URL
    """
    if isinstance(object, ndb.Key):
        kind = object.kind()
        if kind in admin_views:
            return flask.url_for(admin_views[kind], urlsafe=object.urlsafe())
        else:
            return None
    elif hasattr(object, 'key'):
        return get_object_view(object.key)
    else:
        return None


@app.context_processor
def add_object_url():
    """
    Adds the get_object_view function to the template context.
    """
    return dict(
        get_object_view=get_object_view
    )


def quickstart_admin_model(admin_model, name, location, menu_section=None, enable_list=True, enable_retrieve=True, enable_delete=True, enable_edit=True,
                           enable_new=True, exclude=None, list_fields=None, wtforms_field_args=None, form_include=None):
    """
    Quickly registers an ndb model for inclusion in the admin gui with full CRUD.

    :param admin_model: NDB Model class
    :param name: Name for blueprint
    :param location: URL prefix. Eg, 'foo' becomes '/admin/foo'
    :param menu_section: If specified, puts in a submenu by this name.

    :param enable_list: Whether to include a list in the CRUD.
    :param enable_retrieve: Whether to include a list in the CRUD.
    :param enable_delete: Whether to include deletion in the CRUD.
    :param enable_edit: Whether to include modification view in the CRUD.

    :param exclude: List of fields to exclude
    """

    if not exclude:
        exclude = []

    # This is because if we just do "enable_list = enable_list" inside the class, it confuses Python's scoping.
    _enable_list = enable_list
    _enable_retrieve = enable_retrieve
    _enable_delete = enable_delete
    _enable_edit = enable_edit
    _enable_new = enable_new
    _list_fields = list_fields
    _wtforms_field_args = wtforms_field_args
    _form_include = form_include

    class QuickBlueprint(GenericCrud):
        model = admin_model
        base_template = 'admin/admin-base.html'

        extra_context = {'navbar': navbar}

        decorators = [admin_required]

        enable_list = _enable_list
        enable_retrieve = _enable_retrieve
        enable_delete = _enable_delete
        enable_edit = _enable_edit
        enable_new = _enable_new

        form_exclude = ['class'] + exclude
        form_include = _form_include
        list_fields = _list_fields
        wtforms_field_args = _wtforms_field_args

    blueprint = QuickBlueprint(name, name)
    app.register_blueprint(blueprint, url_prefix='/admin/%s' % location)
    if menu_section:
        submenu = navbar.get_submenu(menu_section)
        submenu.add_link(name.title(), '/admin/%s' % location)
    else:
        navbar.add_link(name.title(), '/admin/%s' % location)

    admin_views[admin_model._get_kind()] = '%s.retrieve' % name
