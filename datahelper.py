"""
Just some useful Flask stuff for ndb.
"""
from google.appengine.ext import ndb
from flask import g

from app import app


def put_later(*objs):
    """
    Any ndb model instances passed to this method will be put after the flask request has been processed.
    """
    for obj in objs:
        if obj not in g.dirty_ndb:
            g.dirty_ndb.append(obj)

@app.after_request
def store_ndb(response):
    """
    Puts the contents of g.dirty_ndb
    """
    if g.dirty_ndb:
        ndb.put_multi(g.dirty_ndb)
        g.dirty_ndb = []
    return response

