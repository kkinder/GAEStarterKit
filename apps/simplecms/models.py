"""
Simple way of creating pages on a site.
"""
import hashlib

from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel
from markupsafe import Markup

import markdown

from util.BaseModel import BaseModel
from util.richfields import MarkdownProperty


class Page(BaseModel, PolyModel):
    """
    Each of these (might) represent a page shown to users.
    """
    MARKDOWN = 'Markdown'
    HTML = 'HTML'

    location = ndb.StringProperty(required=True)

    title = ndb.StringProperty()

    meta_author = ndb.StringProperty()
    meta_description = ndb.TextProperty()
    meta_keywords = ndb.TextProperty()

    content = MarkdownProperty(indexed=False, required=True)

    rendered = ndb.TextProperty(indexed=False)
    rendered_hash = ndb.StringProperty()

    def get_rendered_content(self):
        content_md5 = hashlib.md5(self.content).hexdigest()
        if content_md5 != self.rendered_hash:
            self._render_markdown(content_md5)
            self.put()
        return Markup(self.rendered)

    def _render_markdown(self, content_md5):
        self.rendered = markdown.Markdown().convert(self.content)
        self.rendered_hash = content_md5

    def __unicode__(self):
        return self.location
