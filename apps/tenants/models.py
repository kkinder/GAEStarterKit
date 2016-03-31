from google.appengine.ext import ndb

from util.BaseModel import BaseModel


class Tenant(BaseModel, ndb.Model):
    name = ndb.StringProperty()
    owner = ndb.KeyProperty(kind='UserAccount', required=True)

    def __unicode__(self):
        return self.name


class TenantMembership(BaseModel, ndb.Model):
    PRIVILEGE_USER = 'user'
    PRIVILEGE_ADMIN = 'admin'
    PRIVILEGE_OWNER = 'owner'

    tenant = ndb.KeyProperty(kind=Tenant, required=True)
    user = ndb.KeyProperty(kind='UserAccount')
    user_type = ndb.StringProperty(choices=[PRIVILEGE_OWNER, PRIVILEGE_ADMIN, PRIVILEGE_USER], required=True, default=PRIVILEGE_USER)

    invite_token = ndb.StringProperty()
    invite_token_expire = ndb.DateTimeProperty()
    invite_email = ndb.StringProperty()

    def __unicode__(self):
        return u'%s: %s (%s)' % (self.tenant.get(), self.user.get(), self.user_type)
