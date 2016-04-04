"""
Decorators useful for dealing with multi-tenancy.
"""

from functools import wraps

from .models import Tenant
from flask import g, request, redirect, url_for, session


def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_account and g.current_tenant:
            #
            # User is logged in and current tenant is known.
            return f(*args, **kwargs)
        elif g.current_account:
            #
            # User is logged in and current tenant is not known.

            memberships = g.current_account.get_tenant_memberships()
            if memberships.count() == 0:
                #
                # User does not have a tenant account setup. Prompt user to set one up.
                session['post-tenant-view'] = request.url_rule.endpoint

                return redirect(url_for('tenants.setup_tenant'))
            elif memberships.count() == 1:
                #
                # User has exactly one tenant, so we don't have to ask which one.
                for membership in memberships:
                    g.current_tenant = membership.tenant.get()
                    session['current_tenant'] = g.current_tenant.key.urlsafe()
                    return f(*args, **kwargs)
            else:
                #
                # User has multiple tenant memberships, and we have to ask them to choose which one to use.
                session['post-tenant-view'] = request.url_rule.endpoint
                return redirect(url_for('tenants.choose'))
        else:
            #
            # User is not logged in.
            session['post-auth-view'] = request.url_rule.endpoint
            return redirect(url_for('users.login'))
    return decorated_function
