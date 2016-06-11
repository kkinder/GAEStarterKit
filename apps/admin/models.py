from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel

from util.BaseModel import BaseModel


class Activity(BaseModel, PolyModel):
    user = ndb.KeyProperty(kind='UserAccount')
    subject = ndb.KeyProperty()
    type = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)

    searching_enabled = False

    def __str__(self):
        if self.user:
            user = self.user.get()
        else:
            user = '<No one>'

        if self.subject:
            subject = self.subject.get()
        else:
            subject = ''

        return u'%s: %s[%s] <%s>' % (user, subject, self.type, self.tags)
