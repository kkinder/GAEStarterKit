import time
import datetime

import flask
from google.appengine.ext.ndb import put_multi

from GenericViews.GenericList import GenericList
from GenericViews.GenericEditExisting import GenericEditExisting
from flask.ext.babel import gettext
from flask import g

import config
from apps.admin.register import quickstart_admin_model
from .models import TenantMembership
from apps.tenants.decor import tenant_required
from apps.tenants import blueprint
from apps.users.decor import account_required
from flask.ext.login import login_user
from datahelper import put_later
from util import flasher

_ = gettext


def redirect_to_view():
    if 'post-tenant-view' in flask.session:
        view = flask.session['post-tenant-view']
        del flask.session['post-tenant-view']
        return flask.redirect(flask.url_for(view))
    else:
        return flask.redirect(flask.url_for('tenants.tenant_overview'))


class ListMembers(GenericList):
    model = TenantMembership
    name_singular = 'member'
    name_plural = 'members'
    inline_template = 'show-tenant-member.html'

    render_as = 'list'

    decorators = [tenant_required]

    def get_query(self):
        q = super(ListMembers, self).get_query()
        q = q.filter(TenantMembership.tenant == g.current_tenant.key).filter(TenantMembership.is_active == True)
        return q


class EditMember(GenericEditExisting):
    model = TenantMembership
    name_singular = 'member'
    name_plural = 'members'
    inline_template = 'show-tenant-member.html'

    decorators = [tenant_required]
    form_include = ['user_type']

    def fetch_object(self, urlsafe):
        member = super(EditMember, self).fetch_object(urlsafe)
        if not member.is_active:
            return flask.abort(404)
        if member.tenant != g.current_tenant.key:
            return flask.abort(403)
        if member.user == g.current_tenant.owner:
            return flask.abort(400)
        return member

    def redirect_after_completion(self):
        return flask.redirect(flask.url_for('tenants.tenant_overview'))


blueprint.add_url_rule('/account/-load-members/', view_func=ListMembers.as_view('list_members'))
blueprint.add_url_rule('/account/members/<urlsafe>', view_func=EditMember.as_view('edit_member'))


def _member_from_urlsafe(urlsafe):
    if not g.current_tenant_membership.can_invite_users():
        return flask.abort(403)

    member = TenantMembership.from_urlsafe(urlsafe)
    if not member:
        return flask.abort(404)
    if member.tenant != g.current_tenant.key:
        return flask.abort(403)
    return member


@blueprint.route('/account/-resend-invite-email/<urlsafe>/', methods=['POST'])
@tenant_required
def resend_email(urlsafe):
    member = _member_from_urlsafe(urlsafe)
    member.send_invite_email()

    return flask.jsonify({'email': 'sent'})


@blueprint.route('/account/-remove-member/<urlsafe>/', methods=['POST'])
@tenant_required
def remove_member(urlsafe):
    member = _member_from_urlsafe(urlsafe)

    member.is_active = False
    member.put()

    return flask.jsonify({'member': 'deactivated'})


@blueprint.route('/account/', methods=['GET', 'POST'])
@tenant_required
def tenant_overview():
    return flask.render_template(
        'tenant-overview.html',
        members_controller=ListMembers,
        list_members_view='tenants.list_members')


@blueprint.route('/account/invite-member/', methods=['GET', 'POST'])
@tenant_required
def invite_member():
    if not g.current_tenant_membership.can_invite_users():
        return flask.abort(403)

    form = InviteMemberForm(flask.request.form)

    if form.validate_on_submit():
        assert isinstance(g.current_tenant, Tenant)

        try:
            member = g.current_tenant.invite_user(
                email=form.email.data,
                user_type=form.user_type.data)
        except MemberAlreadyInvited:
            flasher.error(_('A user with that email address has already been invited or is a current member'))

        flasher.success(_('User Invited'))
        return flask.redirect(flask.url_for('tenants.tenant_overview'))

    return flask.render_template('invite-member.html', form=form)


@blueprint.route('/choose-account/', methods=['GET', 'POST'])
@account_required
def choose():
    """
    Prompts the user to choose which tenant they want to be using
    """
    if 'm' in flask.request.args:
        member = TenantMembership.from_urlsafe(flask.request.args['m'])
        if member:
            if member.user != g.current_account.key:
                flask.abort(404)
            else:
                flask.session['current_tenant'] = member.tenant.urlsafe()
                return redirect_to_view()
        else:
            flask.abort(404)

    memberships = g.current_account.get_tenant_memberships()
    return flask.render_template('choose-tenant.html', memberships=memberships)


@blueprint.route('/accept-invite/<member_id>/<token>/', methods=['GET', 'POST'])
def accept_invite(member_id, token):
    member = TenantMembership.from_urlsafe(member_id)
    if not member:
        time.sleep(config.security_wait)
        return flask.render_template('no-invite-token.html'), 404
    assert isinstance(member, TenantMembership)
    if member.is_token_valid(token):
        # Invite accepted
        if g.current_account:
            member.user = g.current_account.key
            member.put()
            flask.session['current_tenant'] = member.tenant.urlsafe()

            flasher.success(_('Invite accepted'))
            return flask.redirect(flask.url_for('tenants.tenant_overview'))
        else:
            form = ChoosePasswordForm(flask.request.form)
            if form.validate_on_submit():
                account, auth = UserAccount.from_email(member.invite_email, email_is_verified=True)
                auth.email_is_verified = True
                auth.email_verified_date = datetime.datetime.now()
                account.set_password(form.password.data)
                member.user = account.key

                put_multi([account, auth, member])
                login_user(account)
                flasher.success(_('Invite accepted'))
                return flask.redirect(flask.url_for('tenants.tenant_overview'))

            flask.session['current_tenant'] = member.tenant.urlsafe()
            return flask.render_template('invite-accept-choose-password.html', form=form)

    else:
        return flask.render_template('no-invite-token.html'), 404


@blueprint.route('/account/setup/', methods=['GET', 'POST'])
@account_required
def setup_tenant():
    form = TenantSetupForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        name = form.name.data
        tenant = Tenant(name=name, owner=g.current_account.key)
        tenant.put()
        activity = Activity(user=g.current_account.key, subject=tenant.key, type='tenant', tags=['new-tenant'])

        membership = TenantMembership(
            tenant=tenant.key,
            user=g.current_account.key,
            user_type=TenantMembership.PRIVILEGE_OWNER
        )

        # g.current_account.tenant = tenant.key
        # g.current_account.put()

        flask.session['current_tenant'] = tenant.key.urlsafe()

        put_later(g.current_account, activity, membership)

        flasher.info(_('Account Created'))
        return redirect_to_view()
    return flask.render_template('tenant-setup.html', form=form)


from .forms import TenantSetupForm, InviteMemberForm, ChoosePasswordForm
from .models import Tenant, TenantMembership, MemberAlreadyInvited

quickstart_admin_model(Tenant, 'tenantsadmin', 'tenants', 'Tenants')
quickstart_admin_model(TenantMembership, 'tenantmemberships', 'tenantmemberships', 'Tenants', name_plural='Tenant Memberships',
                       name_singular='Tenant Membership')

from apps.users.models import UserAccount
from apps.admin.models import Activity
