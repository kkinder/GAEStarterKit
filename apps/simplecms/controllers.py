import flask

from apps.admin.register import quickstart_admin_model
from .models import Page

from app import app

quickstart_admin_model(Page, 'pages', 'pages', 'Site', exclude=['rendered'],
                       form_include=['location', 'title', 'meta_author', 'meta_keywords', 'meta_description', 'content'])


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    for page in Page.query(Page.location == '/%s' % path):
        return flask.render_template('page.html', page=page)
    if path.endswith('/'):
        for page in Page.query(Page.location == '/%s' % path[0:-1]):
            return flask.redirect(page.location)
    else:
        for page in Page.query(Page.location == '/%s/' % path):
            return flask.redirect(page.location)


    return flask.abort(404)
