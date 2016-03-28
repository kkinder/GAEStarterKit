"""
Handy utility method for figuring out whether the browser has asked for json.

By Armin Ronacher at http://flask.pocoo.org/snippets/45/ (thanks, Armin!)
"""

from flask import request


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']
