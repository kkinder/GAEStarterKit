"""
Decorators and such we add to the universal app.
"""
import datetime

from authomatic.providers.oauth2 import GitHub
from flask import g

from app import app

@app.context_processor
def inject_user():
    """
    Adds user and auth information to flask templates
    """
    return dict(
        current_account=g.current_account
    )


##
## Monkey patch Authomatic with access to github emails.
## Taken from https://github.com/thephpleague/oauth2-client/issues/9
def access(self, url, **kwargs):
    # https://developer.github.com/v3/#user-agent-required
    headers = kwargs["headers"] = kwargs.get("headers", {})
    if not headers.get("User-Agent"):
        headers["User-Agent"] = self.settings.config[self.name]["consumer_key"]

    def parent_access(url):
        return super(GitHub, self).access(url, **kwargs)

    response = parent_access(url)

    # additional action to get email is required:
    # https://developer.github.com/v3/users/emails/
    if response.status == 200:
        email_response = parent_access(url + "/emails")
        if email_response.status == 200:
            response.data["emails"] = email_response.data

            # find first or primary email
            primary_email = None
            for item in email_response.data:
                is_primary = item["primary"]
                if not primary_email or is_primary:
                    primary_email = item["email"]

                if is_primary:
                    break

            response.data["email"] = primary_email
    return response

GitHub.access = access
