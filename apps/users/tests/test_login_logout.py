from tests.Testing import AppEngineTestCase


class EmailSignupTestCase(AppEngineTestCase):
    def _create_user(self, email, password, profile_url, signup_email_url):
        rv = self.client.get(signup_email_url)
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
        # Check to make sure we are logged in
        rv = self.client.get(profile_url)
        self.assertIn(email, rv.data)
        self.assertEqual(rv.status_code, 200)

    def _login_user(self, email, password, login_url):
        rv = self.client.get(login_url)
        token = self.extract_csrf_token(rv)
        rv = self.client.post(login_url, data={
            'email': email,
            'password': password,
            'csrf_token': token,
        })

        if 'invalid email address or password' in rv.data.lower():
            self.fail('User could not login')

        self.assertEqual(rv.status_code, 302)

    def _logout_user(self, login_url, logout_url, profile_url):
        rv = self.client.get(logout_url)
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get(profile_url)
        self.assertEqual(rv.status_code, 302)
        self.assertIn(login_url, rv.location)

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

        email = 'test_%s@testing.com' % self._gen_random_letters()
        password = self._gen_random_letters()

        with self.app.test_request_context(signup_email_url):
            self._create_user(email, password, profile_url, signup_email_url)
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

    def test_login_logout(self):
        signup_email_url = self.url_for('users.signup_email')
        profile_url = self.url_for('users.profile')
        login_url = self.url_for('users.login')
        logout_url = self.url_for('users.logout')

        email = 'test_%s@testing.com' % self._gen_random_letters()
        password = self._gen_random_letters()

        with self.app.test_request_context(signup_email_url):
            self._create_user(email, password, profile_url, signup_email_url)
            self._logout_user(login_url, logout_url, profile_url)

    def test_recover_password(self):
        from apps.email.models import OutboundEmail

        signup_email_url = self.url_for('users.signup_email')
        profile_url = self.url_for('users.profile')
        login_url = self.url_for('users.login')
        logout_url = self.url_for('users.logout')
        forgot_password_url = self.url_for('users.forgot_password')

        email = 'test_%s@testing.com' % self._gen_random_letters()
        original_password = self._gen_random_letters()
        new_password = self._gen_random_letters()

        with self.app.test_request_context(signup_email_url):
            self._create_user(email, original_password, profile_url, signup_email_url)
            self._logout_user(login_url, logout_url, profile_url)

            rv = self.client.get(forgot_password_url)
            token = self.extract_csrf_token(rv)

            rv = self.client.post(forgot_password_url, data={
                'email': email,
                'csrf_token': token,
            })
            self.assertEqual(rv.status_code, 200)

            emails = list(OutboundEmail.query().fetch(1000))
            self.failUnlessEqual(len(emails), 2)

            outbound_email = None
            for e in emails:
                if 'password' in e.subject.lower():
                    outbound_email = e
                    break
            self.assert_(outbound_email, 'Password reset email not found')

            words = outbound_email.text_body.split()
            reset_password_link = ''
            for word in words:
                if 'reset-password' in word:
                    reset_password_link = word
                    break

            self.assert_(reset_password_link, 'Cannot find reset password link in email')

            ##
            ## We have a reset password link. Before trying it, let's try a couple of invalid urls
            reset_link_parts = reset_password_link.split('/')
            reset_link_parts[-2] = reset_link_parts[-2] + 'FOO'
            self.new_client()
            rv = self.client.get('/'.join(reset_link_parts))
            self.failUnlessEqual(404, rv.status_code)

            reset_link_parts = reset_password_link.split('/')
            reset_link_parts[-3] = reset_link_parts[-3] + 'BAR'
            self.new_client()
            rv = self.client.get('/'.join(reset_link_parts))
            self.failUnlessEqual(404, rv.status_code)


            ##
            ## Now try real reset password link.
            self.new_client()
            rv = self.client.get(reset_password_link)
            self.assertEqual(rv.status_code, 200)
            token = self.extract_csrf_token(rv)

            rv = self.client.post(
                reset_password_link,
                data=dict(
                    csrf_token=token,
                    password=new_password,
                    confirm=new_password
                )
            )

            self.assertEqual(rv.status_code, 302)

            self.new_client()
            self._login_user(email, new_password, login_url)
