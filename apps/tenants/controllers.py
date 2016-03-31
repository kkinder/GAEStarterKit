import flask
from apps.admin.register import quickstart_admin_model
from apps.tenants.decor import tenant_required
from flask.ext.babel import gettext
from flask import g

from apps.admin.models import Activity
from apps.tenants import blueprint
from apps.users.decor import account_required
from main import put_later
from util import flasher
from .forms import TenantSetupForm
from .models import Tenant, TenantMembership

_ = gettext


@blueprint.route('/account/', methods=['GET', 'POST'])
@tenant_required
def tenant_overview():
    return 'tenant-overview'






@blueprint.route('/account/setup/', methods=['GET', 'POST'])
@account_required
def setup_tenant():
    form = TenantSetupForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        name = form.name.data
        tenant = Tenant(name=name, owner=g.current_account.key)
        tenant.put()
        activity = Activity(user=g.current_account.key, subject=tenant.key, type='tenant', tags=['new-tenant'])

        g.current_account.tenant = tenant.key
        g.current_account.put()

        put_later(g.current_account, activity)

        flasher.info(_('Account Created'))
        return flask.redirect('/')
    return flask.render_template('tenant-setup.html', form=form)


quickstart_admin_model(Tenant, 'tenants', 'tenants', 'Tenants')
quickstart_admin_model(TenantMembership, 'tenantmemberships', 'tenantmemberships', 'Tenants', name_plural='Tenant Memberships', name_singular='Tenant Membership')
