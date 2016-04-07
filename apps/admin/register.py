from google.appengine.ext import ndb
import flask
from GenericViews import _from_camel

from apps.users.decor import admin_required
from GenericViews.GenericCrud import GenericCrud
from .navigation import Menu

from app import app


class AdminArea(object):
    def __init__(self):
        self.navbar = Menu()
        self.admin_views = {}

    def register_blueprint(self, blueprint, name, friendly_name, location, menu_section=None):
        assert isinstance(blueprint, ModelAdmin)
        blueprint.extra_context['navbar'] = self.navbar
        #blueprint = QuickBlueprint(name, name)
        app.register_blueprint(blueprint, url_prefix='/admin/%s' % location)

        if menu_section:
            submenu = self.navbar.get_submenu(menu_section)
            submenu.add_link(friendly_name, '/admin/%s' % location)
        else:
            self.navbar.add_link(friendly_name, '/admin/%s' % location)

        if blueprint.model._get_kind() in self.admin_views:
            raise ValueError, 'admin view for %r already registered' % (blueprint.model._get_kind(),)
        self.admin_views[blueprint.model._get_kind()] = '%s.retrieve' % name


    def get_object_view(self, object):
        """
        Returns the admin/CRUD view for a particular object, if there is one. The object can be an ndb object, or an ndb key. It assumes the view accepts
        urlsafe (from the key) as a parameter.

        :param object: NDB object or NDB key.
        :return: URL
        """
        if isinstance(object, ndb.Key):
            kind = object.kind()
            if kind in self.admin_views:
                return flask.url_for(self.admin_views[kind], urlsafe=object.urlsafe())
            else:
                return None
        elif hasattr(object, 'key'):
            return self.get_object_view(object.key)
        else:
            return None

admin_area = AdminArea()


@app.context_processor
def add_object_url():
    """
    Adds the get_object_view function to the template context.
    """
    return dict(
        get_object_view=admin_area.get_object_view
    )


class ModelAdmin(GenericCrud):
    base_template = 'admin/admin-base.html'
    extra_context = {}
    decorators = [admin_required]




def quickstart_admin_model(admin_model, name=None, location=None, menu_section=None, **args):
    """
    Quickly registers an ndb model for inclusion in the admin gui with full CRUD.

    :param admin_model: NDB Model class
    :param name: Name for blueprint
    :param location: URL prefix. Eg, 'foo' becomes '/admin/foo'
    :param menu_section: If specified, puts in a submenu by this name.
    """

    if not name:
        name = admin_model.__name__.lower()
    if not location:
        location = name
    #raise ValueError, name

    class QuickBlueprint(ModelAdmin):
        model = admin_model

    for k, w in args.items():
        setattr(QuickBlueprint, k, w)

    if 'name_plural' in args:
        friendly_name = args['name_plural'].title()
    elif 'name_singular' in args:
        friendly_name = args['name_singular'].title()
    else:
        friendly_name = _from_camel(admin_model.__name__).replace('_', ' ').title()

    blueprint = QuickBlueprint(name=name, import_name=name)

    admin_area.register_blueprint(blueprint, name=name, friendly_name=friendly_name, location=location, menu_section=menu_section)
