import datetime

import flask
from google.appengine.ext import ndb

import config
from apps.email import send_email_from_template
from util.BaseModel import BaseModel


class MemberAlreadyInvited(Exception):
    def __init__(self, other_user, *args, **kwargs):
        super(MemberAlreadyInvited, self).__init__(other_user, *args, **kwargs)
        self.other_user = other_user


class Tenant(BaseModel, ndb.Model):
    name = ndb.StringProperty()
    owner = ndb.KeyProperty(kind='UserAccount', required=True)

    def get_memberships(self):
        return TenantMembership.query().filter(TenantMembership.tenant==self.key)

    def __unicode__(self):
        return self.name

    def invite_user(self, email, user_type, send_email=True):
        q = TenantMembership.query().filter(TenantMembership.invite_email == email)
        if q.count() > 0:
            for other_user in q:
                raise MemberAlreadyInvited(other_user=other_user)
        member = TenantMembership(tenant=self.key, user_type=user_type, invite_email=email)
        member.generate_invite_tokens()
        member.put()
        if send_email:
            member.send_invite_email()
        return member


class TenantMembership(BaseModel, ndb.Model):
    PRIVILEGE_USER = 'user'
    PRIVILEGE_ADMIN = 'admin'
    PRIVILEGE_OWNER = 'owner'
    USER_TYPES = [PRIVILEGE_OWNER, PRIVILEGE_ADMIN, PRIVILEGE_USER]
    USER_TYPE_CHOICES = [(t, t.title()) for t in USER_TYPES]

    tenant = ndb.KeyProperty(kind=Tenant, required=True)
    user = ndb.KeyProperty(kind='UserAccount')
    user_type = ndb.StringProperty(choices=USER_TYPES, required=True, default=PRIVILEGE_USER)

    invite_token = ndb.StringProperty()
    invite_token_expire = ndb.DateTimeProperty()
    invite_email = ndb.StringProperty()

    invite_sent = ndb.DateTimeProperty()

    def __unicode__(self):
        if self.user and self.user.get():
            return u'%s: %s (%s)' % (self.tenant.get(), self.user.get(), self.user_type)
        else:
            return u'%s: %s (pending) %s' % (self.tenant.get(), self.invite_email, self.user_type)

    def is_token_valid(self, token):
        """
        Returns True if the invitation goes through. False if not.
        """
        if self.invite_token_expire and self.invite_token_expire > datetime.datetime.now():
            return False
        elif self.invite_token == token:
            return True
        else:
            return False

    def generate_invite_tokens(self, expires=None):
        self.invite_token = self._generate_token()
        if expires:
            self.invite_token_expire = expires

    def send_invite_email(self):
        if not self.invite_token:
            raise ValueError, 'No invite token found'

        send_email_from_template(
            'email/invite-member',
            from_address=config.email_from_address,
            to_address=self.invite_email,
            accept_link=flask.url_for('tenants.accept_invite', member_id=self.key.urlsafe(), token=self.invite_token)
        )
