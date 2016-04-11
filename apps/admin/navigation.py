"""
Handles building the admin area navigation rather nicely.
"""
from collections import OrderedDict


class MenuItemBase(object):
    item_type = None


class MenuLink(MenuItemBase):
    item_type = 'link'

    def __init__(self, label, location, icon=None):
        self.label = label
        self.location = location
        self.icon = icon


class MenuSeparator(MenuItemBase):
    item_type = 'separator'


class Menu(MenuItemBase):
    item_type = 'menu'

    def __init__(self, label=None):
        self.label = label
        self.children = []

    def add_child(self, child):
        assert isinstance(child, MenuItemBase)
        self.children.append(child)

    def add_separator(self):
        self.add_child(MenuSeparator)

    def add_link(self, label, location, icon=None):
        self.add_child(MenuLink(label=label, location=location, icon=icon))

    def get_submenu(self, label):
        for child in self.children:
            if isinstance(child, Menu) and child.label == label:
                return child
        menu = Menu(label=label)
        self.add_child(menu)
        return menu
