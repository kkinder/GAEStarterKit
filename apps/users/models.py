import datetime
import hashlib
import random
from string import ascii_letters as alphabet

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel

import authomatic
import config
import flask
from apps.admin.models import Activity
from apps.email import send_email_from_template
from flask.ext.babel import gettext as _
from datahelper import put_later
from util.BaseModel import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash


class UserAuth(BaseModel, PolyModel):
    auth_type = None

    name = ndb.StringProperty()
    email = ndb.StringProperty()
    is_primary = ndb.ComputedProperty(lambda self: self.get_is_primary())

    local_data = ndb.JsonProperty()

    user_account = ndb.KeyProperty(kind='UserAccount')

    ##
    ## Account status
    def set_primary(self):
        account = self.user_account.get()
        account.primary_auth = self.key
        put_later(account)

    def get_is_primary(self):
        if self.user_account:
            return self.user_account.get().primary_auth == self.key
        else:
            return True

    def __unicode__(self):
        return '%s <%s> [%s]' % (self.name or '(No Name)', self.email, self.auth_type)

    __repr__ = __unicode__


class EmailAuth(UserAuth):
    auth_type = 'email'

    verification_token = ndb.StringProperty()
    verification_token_created = ndb.DateTimeProperty()

    email_is_verified = ndb.BooleanProperty(required=True)
    email_verified_date = ndb.DateTimeProperty()

    def is_verified(self):
        return self.email_is_verified

    def is_trusted(self):
        return self.email_is_verified

    ##
    ## Methods relating to email verification
    def send_verification_email(self):
        """
        Sends user the verification email. NOTE: This method does not generate the token itself.
        """
        if not self.verification_token:
            raise ValueError('Verification token not set')

        send_email_from_template(
            'email/verification', config.email_from_address, self.email,
            verification_link=flask.url_for('users.verify', auth_id=self.key.urlsafe(), token=self.verification_token)
        )

    def verify_email(self, token, put=True):
        """
        Call this method to verify a user's email address

        :param token: Verification token

        :param put: If True, object will be updated automatically in ndb. Otherwise, the caller must save the object.

        :return: If verification succeeded, returns True. Otherwise, returns False
        """
        if not token:
            return False
        elif not self.verification_token:
            return False
        elif (datetime.datetime.now() - self.verification_token_created).days > config.max_days_verification:
            return False
        elif self.verification_token != token:
            return False
        else:
            self.email_is_verified = True
            self.email_verified_date = datetime.datetime.now()
            self.verification_token = None
            self.verification_token_created = None
            if put:
                self.put()
            return True

    def send_recovery_email(self, reset_token):
        send_email_from_template(
            'email/reset', config.email_from_address, self.email,
            reset_link=flask.url_for('users.reset_password', auth_id=self.key.urlsafe(), token=reset_token)
        )

    @classmethod
    def from_email(cls, email, create=True, email_is_verified=False):
        auth = cls.get_by_id(email.strip().lower())
        if auth is None and create:
            if not email_is_verified:
                verification_token = cls._generate_token()
                verification_token_created = datetime.datetime.now()
            else:
                verification_token = None
                verification_token_created = None

            obj = cls.get_or_insert(
                email.strip().lower(),
                verification_token=verification_token,
                verification_token_created=verification_token_created,
                email_is_verified=email_is_verified,
                email=email)
            if not email_is_verified:
                obj.send_verification_email()
            return obj
        return auth


class GoogleAuth(UserAuth):
    auth_type = 'google'

    google_id = ndb.StringProperty()

    def is_verified(self):
        return False

    def is_trusted(self):
        return True

    @classmethod
    def _from_google(cls, google_user):
        assert isinstance(google_user, users.User)

        ##
        ## Generate a unique ID we can use.
        user_id = google_user.user_id()
        if not user_id:
            user_id = 'email-hash-%s' % hashlib.md5(google_user.email()).hexdigest()
        full_id = 'google-{}'.format(user_id)

        google_auth = cls.get_or_insert(
            full_id,
            google_id=user_id
        )

        google_auth.name = google_user.nickname()
        google_auth.email = google_user.email()
        return google_auth


class AuthomaticAuth(UserAuth):
    auth_type = 'openid'

    authomatic_user_id = ndb.StringProperty()
    authomatic_provider = ndb.StringProperty()
    authomatic_credentials = ndb.TextProperty()

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    nickname = ndb.StringProperty()
    link = ndb.StringProperty()
    gender = ndb.StringProperty()
    timezone = ndb.StringProperty()
    locale = ndb.StringProperty()
    phone = ndb.StringProperty()
    picture = ndb.StringProperty()
    birth_date_parsed = ndb.StringProperty()
    birth_date_unparsed = ndb.StringProperty()
    country = ndb.StringProperty()
    city = ndb.StringProperty()
    location = ndb.StringProperty()
    postal_code = ndb.StringProperty()

    extra_data = ndb.JsonProperty()

    @classmethod
    def _from_authomatic(cls, authomatic_user, provider_code):
        assert isinstance(authomatic_user, authomatic.core.User)

        full_id = 'authomatic-{provider}-{user_id}'.format(
            provider=provider_code,
            user_id=authomatic_user.id)

        authomatic_auth = cls.get_or_insert(
            full_id,
            authomatic_user_id=authomatic_user.id,
            authomatic_provider=str(provider_code),
            authomatic_credentials=authomatic_user.credentials.serialize()
        )

        authomatic_auth.email = authomatic_user.email
        authomatic_auth.name = authomatic_user.name

        authomatic_auth.extra_data = authomatic_user.data

        for k in ('first_name', 'last_name', 'nickname', 'link', 'gender', 'timezone', 'locale', 'picture'):
            setattr(authomatic_auth, k, getattr(authomatic_user, k, None))
        if authomatic_user.birth_date and isinstance(authomatic_user.birth_date, datetime.datetime):
            authomatic_auth.birth_date_parsed = authomatic_user.birth_date
            authomatic_auth.birth_date_unparsed = None
        elif authomatic_user.birth_date:
            authomatic_auth.birth_date_parsed = None
            authomatic_auth.birth_date_unparsed = authomatic_user.birth_date

        return authomatic_auth


class UserAccount(BaseModel, ndb.Model):
    is_superuser = ndb.BooleanProperty(required=True, default=False)
    is_enabled = ndb.BooleanProperty(required=True, default=True)

    primary_auth = ndb.KeyProperty(UserAuth)
    email = ndb.ComputedProperty(lambda self: self.get_email())
    authentication_methods = ndb.ComputedProperty(lambda self: self.get_authentication_methods())
    display_name = ndb.ComputedProperty(lambda self: self.get_display_name())
    tenant_count = ndb.ComputedProperty(lambda self: self.get_tenant_memberships().count())

    name = ndb.StringProperty()

    password_hash = ndb.StringProperty()

    reset_token = ndb.StringProperty()
    reset_token_created = ndb.DateTimeProperty()

    def get_tenant_memberships(self):
        """
        Gets tenant memberships for a particular user. This is the preferred method over querying directly.
        """
        return TenantMembership.query().filter(TenantMembership.user == self.key)

    def get_membership_for_tenant(self, tenant):
        if isinstance(tenant, ndb.Key):
            tenant = tenant.get()

        is_owner = tenant.owner == self

        membership = TenantMembership.query().filter(TenantMembership.user == self.key, TenantMembership.tenant == tenant.key).get()

        # raise ValueError, [membership, self.get_tenant_memberships().fetch(100)]

        if is_owner and not membership:
            membership = TenantMembership(tenant=tenant, user=self, user_type=TenantMembership.PRIVILEGE_OWNER)
            membership.put()
        return membership

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash or '', password)

    def get_authentication_methods(self):
        return ' '.join([a.auth_type for a in self.get_auths()])

    def get_auths(self):
        return UserAuth.query(UserAuth.user_account == self.key).fetch(9999)

    def get_display_name(self):
        if self.name:
            return self.name

        elif self.primary_auth:
            auth = self.primary_auth.get()
            if auth.name:
                return auth.name
            elif auth.email:
                return auth.email

        return _('<Unknown User>')

    def get_email(self):
        if self.primary_auth:
            auth = self.primary_auth.get()
            return auth.email
        else:
            return None

    ##
    ## Methods related to recovering lost passwords
    def recover_password(self, put=True, send_email=True):
        """
        Generate password recovery code and optionally send an email to the user with the verification link.

        :param put: If True, object will be updated automatically in ndb. Otherwise, the caller must save the object.

        :param send_email: If True, a recovery email will be sent to the account.
        """
        self.reset_token = EmailAuth._generate_token()
        self.reset_token_created = datetime.datetime.now()
        if put:
            self.put()
        if send_email:
            self.primary_auth.get().send_recovery_email(self.reset_token)

    def verify_reset_password(self, token):
        """
        Call when a user wants to reset their password and has received a verification token via email.

        :param token: Reset token

        :return: If token is valid, returns True.
        """
        if not token:
            return False
        if not self.reset_token:
            return False
        if (datetime.datetime.now() - self.reset_token_created).seconds > (config.max_hours_password_reset * 3600):
            return False
        elif self.reset_token != token:
            return False
        else:
            return True

    @classmethod
    def _init_auth(cls, auth):
        if auth.user_account:
            account = auth.user_account.get()
        else:
            account = UserAccount()
            account.put()
        auth.user_account = account.key
        if not account.primary_auth:
            if not auth.key:
                auth.put()
            account.primary_auth = auth.key

        activity = Activity(user=account.key, subject=account.key, type='account', tags=['new-signup'])

        put_later(account, auth, activity, activity)
        return account

    @classmethod
    def from_email(cls, email, email_is_verified=False):
        return cls.from_email_auth(EmailAuth.from_email(email, email_is_verified=email_is_verified))

    @classmethod
    def from_email_auth(cls, email_auth):
        assert isinstance(email_auth, EmailAuth)
        account = cls._init_auth(email_auth)
        return account, email_auth

    @classmethod
    def from_google(cls, google_user, is_superuser):
        auth = GoogleAuth._from_google(google_user)
        account = cls._init_auth(auth)
        account.is_superuser = is_superuser
        return account, auth

    @classmethod
    def from_authomatic(cls, authomatic_user, provider_code):
        auth = AuthomaticAuth._from_authomatic(authomatic_user, provider_code)
        account = cls._init_auth(auth)
        return account, auth

    def get_picture(self):
        if self.email:
            return 'https://www.gravatar.com/avatar/{}.jpg?s=250&d=mm'.format(hashlib.md5(self.email).hexdigest())
        else:
            return None

    def __unicode__(self):
        if self.display_name and self.email and self.email != self.display_name:
            return '%s <%s>' % (self.display_name, self.email)
        elif self.email:
            return self.email
        elif self.display_name:
            return self.display_name
        else:
            print '<Unknown user %r>' % (self.key.id())

    #
    # For flask_login
    def get_id(self):
        return self.key.urlsafe()

    def is_verified(self):
        return False

    def is_trusted(self):
        return self.is_superuser

    is_anonymous = False
    is_authenticated = True

    @property
    def is_active(self):
        return self.is_enabled


from apps.tenants.models import TenantMembership, Tenant
