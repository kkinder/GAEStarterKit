"""
GenericViews, inspired by Django's rather handy system of generic views, reduces the tedium of web-based software.

You can individually use classes like GenericRetrieve, GenericList, etc, or use GenericCrud to quickly create a full create/retrieve/update/delete/list
set of views, all nicely packaged.
"""
import re


def _from_camel(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
