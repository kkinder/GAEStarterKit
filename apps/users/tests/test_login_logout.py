from tests.Testing import AppEngineTestCase


class EmailSignupTestCase(AppEngineTestCase):
    def test_login_redirect(self):
        profile_url = self.url_for('users.profile')
        login_url = self.url_for('users.login')

        rv = self.get_page(profile_url)
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location.split('?')[0], 'http://localhost%s' % login_url)

        rv = self.get_page(rv.location)
        self.assertEqual(rv.status_code, 200)


    def test_signup_email(self):
        from apps.users.models import UserAccount
        signup_email_url = self.url_for('users.signup_email')
        profile_url = self.url_for('users.profile')

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
            self.assertEqual(rv.location, 'http://localhost%s' % profile_url)

            #
            # Account exists. Try confirming it.
            q = UserAccount.query()
            all_accounts = q.fetch(1000)
            self.failUnlessEqual(len(all_accounts), 1)
            put_account = all_accounts[0]

            self.failUnlessEqual(put_account.email, email)

            auths = put_account.get_auths()
            self.assertEqual(len(auths), 1)
            auth = auths[0]

            self.assertEqual(auth.email, email)
            self.assertEqual(auth.email_is_verified, False)

            self.assert_(not auth.verify_email('asdfasdf'))
            self.assertEqual(auth.email_is_verified, False)

            self.assert_(auth.verify_email(auth.verification_token))
            self.assertEqual(auth.email_is_verified, True)
