"""
Contains various classes that specify to the crud components the nature of various fields
"""
from google.appengine.ext import ndb


class MarkdownProperty(ndb.TextProperty):
    pass
