from tests.Testing import AppEngineTestCase

class WelcomeKitTestCase(AppEngineTestCase):
    def test_welcome_page(self):
        rv = self.get_page('/')
        self.assertEqual(rv.status_code, 200)
