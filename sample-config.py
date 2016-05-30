# -*- coding: utf-8 -*-
"""
Example configuration for GEAStarterKit
"""

##
## Authentication/authorizationc config
import authomatic

from authomatic.providers import oauth2
from collections import OrderedDict

AUTHOMATIC_CONFIG = OrderedDict([
    ('google', {
        'name': 'Google',

        'id': 1000,

        'icon': 'google'
    }),

    # ('github', {
    #     'name': 'Github',
    #
    #     'class_': oauth2.GitHub,
    #     'consumer_key': 'ADD YOURS',
    #     'consumer_secret': 'AD YOURS',
    #
    #     'id': 2000,
    #
    #     'icon': 'github',
    #
    #     'scope': ['user:email']
    # }),

])

import os
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development') or os.environ.get('SERVER_SOFTWARE', '') == '':
    SECRET_STRING = 'YOUR SECRET KEY'
    DEVELOPMENT = True
else:
    SECRET_STRING = 'YOUR SECRET KEY'
    DEVELOPMENT = False

#
# Talisman security
import talisman

csp_policy = {
    # Fonts from fonts.google.com
    'font-src': "'self' themes.googleusercontent.com *.gstatic.com",
    # <iframe> based embedding for Maps and Youtube.
    'frame-src': "'self' www.google.com www.youtube.com",
    # Assorted Google-hosted Libraries/APIs.
    'script-src': "'self' ajax.googleapis.com *.googleanalytics.com "
                  "*.google-analytics.com",
    # Used by generated code from http://www.google.com/fonts
    'style-src': "'self' ajax.googleapis.com fonts.googleapis.com "
                 "*.gstatic.com",

    # gravatar
    'img-src': "'self' *.gravatar.com",

    # Other
    'default-src': "'self' *.gstatic.com",
}

enable_talisman = True
talisman_config = dict(
    force_https=True,
    force_https_permanent=False,
    frame_options=talisman.SAMEORIGIN,
    frame_options_allow_from=None,
    strict_transport_security=True,
    strict_transport_security_max_age=31556926,  # One year in seconds
    strict_transport_security_include_subdomains=True,
    content_security_policy=csp_policy,
    session_cookie_secure=True,
    session_cookie_http_only=True
)


#
# Origin address for system emails.
email_from_address = 'root@localhost'

#
# Options for login manager
max_days_verification = 30
max_hours_password_reset = 48

#
# How long to time.sleep() when an invalid login, token, or similar is tried.
security_wait = 3

#
# Languages application supports
languages = OrderedDict([
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français')
])

#
# Whether to use Paste debug panel while in development
enable_debug_panel = DEVELOPMENT

#
# Where to send user when he logs in if nothing else is set.
default_view = 'users.profile'

#
# Name of the site/product
site_name = 'GAEStarterKit'

#
# Domain name for email links
email_domain = 'http://localhost:8080'

#
# What to import automatically
install_apps = [
    'apps.welcomekit',
    'apps.simplecms',
    'apps.error_pages',
    'apps.users',
    'apps.tenants',
    'apps.email',
    'apps.admin',
]
