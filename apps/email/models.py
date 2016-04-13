"""
Data side of email framework. Optionally, outbound emails can be saved, or queued, in the OutboundEmail model.
"""

import datetime

from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel

from util.BaseModel import BaseModel
from util.richfields import RenderedHtmlProperty, FormattedTextProperty


class OutboundEmail(BaseModel, PolyModel):
    """
    Functions as both a queue for outbound emails, as well as a useful debug tool.
    """
    from_address = ndb.StringProperty()
    to_address = ndb.StringProperty()
    subject = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    sent = ndb.DateProperty()

    html_body = RenderedHtmlProperty()
    text_body = FormattedTextProperty()

    sent_via = ndb.StringProperty()

    def deliver(self, put=True):
        self.deliver_appengine(put=put)

    def deliver_appengine(self, put=True):
        """
        Deliver via App Engine API.
        """
        message = mail.EmailMessage(sender=self.from_address,
                                    subject=self.subject,
                                    to=self.to_address)

        if self.text_body:
            message.body = self.text_body
        if self.html_body:
            message.html = self.html_body

        message.send()

        self.sent_via = 'appengine'
        self.sent = datetime.datetime.now()
        if put:
            self.put()

    def __unicode__(self):
        return u'%s | %s' % (self.subject, self.to_address)
