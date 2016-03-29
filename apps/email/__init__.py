"""
Handles emails sent from app to users/admins. The intended way to send emails is by calling, simply, the send_email_from_template method.
"""
import flask

import models
import controllers

def send_email_from_template(template_prefix, from_address, to_address, **context):
    """
    Uses flask templates to generic and send emails, using whatever method (app engine, sendgrid, etc) the application is configured for.

    What's clever is the use of templates. For example, if you pass 'forgot-password' as the template_prefix, the method actually uses THREE separate templates
    to generate the outbound email. It finds, 'forgot-password.html' for the body of the html message, 'forgot-password.text' for the text-only version of
    the email, and finally, 'forgot-password.subject' for the subject of the outbound email.

    :param template_prefix: Template prefix to figure out other templates from ('.subject', '.text', '.html')
    :param from_address: From address of email. May include name, eg, "My Company <noreply@example.com>"
    :param to_address: To address of email. May include name, eg, "Customer Person <name@example.com>"
    :param context: Variables to pass to each template
    :return: Key of Outbound email created.
    """
    subject = flask.render_template(template_prefix + '.subject', **context)
    text = flask.render_template(template_prefix + '.text', **context)
    html = flask.render_template(template_prefix + '.html', **context)

    message = models.OutboundEmail()
    message.from_address = from_address
    message.to_address = to_address
    message.subject = subject
    message.html_body = html
    message.text_body = text
    message.put()
    return message.key
