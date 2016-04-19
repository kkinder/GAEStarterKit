#
# Fix PyCharm's wrong-headed idea that the "find" directory should be here.
def fixPyCharmPath():
    import sys, os
    import apps
    for path in apps.__path__:
        if path in sys.path:
            sys.path.remove(path)
        if os.path.abspath(path) in sys.path:
            sys.path.remove(os.path.abspath(path))
fixPyCharmPath()

import random
import string
import unittest
import warnings

from google.appengine.ext import testbed
from flask import wrappers, url_for


class AppEngineTestCase(unittest.TestCase):
    dev_appserver_fixed = False

    def extract_csrf_token(self, rv):
        for content in rv.response:
            c = content.split()
            if 'x_find_csrf_token' in c:
                return c[c.index('x_find_csrf_token')+1]


    def url_for(self, *args, **kwargs):
        with self.app.test_request_context('/'):
            return url_for(*args, **kwargs)

    def _gen_random_letters(self, length=5):
        r = random.SystemRandom()
        return ''.join(r.choice(string.letters) for _ in range(length))


    def setUp(self):
        from main import app
        if not AppEngineTestCase.dev_appserver_fixed:
            warnings.filterwarnings('ignore', category=UserWarning)

            import appengine_config
            appengine_config.PRODUCTION_MODE = False
            import dev_appserver
            dev_appserver.fix_sys_path()
            AppEngineTestCase.dev_appserver_fixed = True

        # Flask apps testing. See: http://flask.pocoo.org/docs/testing/
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        self.app = app
        self.client = app.test_client()

        # Setups app engine test bed. See: http://code.google.com/appengine/docs/python/tools/localunittesting.html#Introducing_the_Python_Testing_Utilities
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_urlfetch_stub()

        import datahelper
        datahelper.put_later = self.put_later

        self.dirty_ndb = []

    def put_later(self, *args):
        self.dirty_ndb += args

    def trigger_put_later(self):
        from google.appengine.ext import ndb

        ndb.put_multi(*self.dirty_ndb)
        self.dirty_ndb = []

    def tearDown(self):
        self.testbed.deactivate()

    def get_page(self, url):
        rv = self.client.get(url)
        assert isinstance(rv, wrappers.Response)
        return rv


if __name__ == '__main__':
    unittest.main()
