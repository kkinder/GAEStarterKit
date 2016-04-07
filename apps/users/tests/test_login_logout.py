from tests.Testing import AppEngineTestCase

class EmailSignupTestCase(AppEngineTestCase):
    def test_login_redirect(self):
        profile_url = self.url_for('users.profile')
        rv = self.get_page(profile_url)
        self.assertEqual(rv.status_code, 302)

        rv = self.get_page(rv.location)

        self.assertEqual(rv.status_code, 200)

    def test_signup_email(self):
        #profile_url = self.url_for('users.profile')
        signup_email_url = self.url_for('users.signup_email')

        with self.app.test_request_context(signup_email_url):
            rv = self.client.get(signup_email_url)

            email = 'test_%s@testing.com' % self._gen_random_letters()
            password = self._gen_random_letters()

            token = self.extract_csrf_token(rv)

            rv = self.client.post(signup_email_url, data={
                'email': email,
                'csrf_token': token,
                'password': password,
                'confirm': password,
                'accept_tos': 'checked'
            })

            self.assertEqual(rv.status_code, 302)
