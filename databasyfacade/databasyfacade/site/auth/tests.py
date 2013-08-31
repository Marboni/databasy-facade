import lxml.html
from flask import url_for
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.services import auth_service, profiles_service, models_service
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData, InvitationData, ModelInfoData
from databasyfacade.utils import tokens

__author__ = 'Marboni'

class AuthTest(DatabasyTest):
    def _test_sign_up_and_activate(self, sign_up_url):
        with self.mail.record_messages() as outbox:
            response = self.client.post(sign_up_url, data={
                'username': 'Boris',
                'email': 'BMarchenko@databasy.com',
                'password': 'password',
                'password_again': 'password'
            })
            self.assert200(response)
            self.assertTrue('BMarchenko@databasy.com' in response.data)

            try:
                auth_service.user_by_username_or_email('BoriS')
                user = auth_service.user_by_username_or_email('bMarchenko@databasy.com')
            except NoResultFound:
                self.fail('User not created.')

            self.assertEqual('Boris', user.username)
            self.assertEqual('boris', user.username_lower)
            self.assertEqual('bmarchenko@databasy.com', user.email_lower)
            self.assertTrue(user.check_password('password'))
            self.assertFalse(user.active)

            try:
                profile = profiles_service.profile(user.id)
                self.assertEqual('BMarchenko@databasy.com', profile.email)
            except NoResultFound:
                self.fail('Profile not created.')

            user_tokens = tokens.user_tokens(user.id)
            self.assertEqual(1, len(user_tokens))
            token = user_tokens[0]
            activation_link = '/auth/activate/?token=%s' % token.hex
            callback_url = self.app.config['ENDPOINT'] + activation_link

            self.assertEqual(1, len(outbox))
            message = outbox[0].body
            self.assertTrue('Boris' in message)
            self.assertTrue(callback_url in message)

            inactive_login_response = self.client.post(url_for('auth.login'), data={
                'username_or_email': user.email_lower,
                'password': 'password'
            })
            self.assert_200(inactive_login_response)
            self.assertNotAuthenticated()

            response = self.client.get(activation_link)
            self.assertRedirects(response, url_for('root.home'))
            self.assertAuthenticated()

    def test_sign_up_from_welcome_and_activate(self):
        self._test_sign_up_and_activate(url_for('root.home'))

    def test_sign_up_and_activate(self):
        self._test_sign_up_and_activate(url_for('auth.sign_up'))

    @fixtures(UserData, ProfileData, ModelInfoData, InvitationData)
    def test_sign_up_by_invitation(self, data):
        response = self.client.get(url_for('auth.sign_up') + '?invitation=' + InvitationData.invitation.hex)
        self.assert200(response)
        html = lxml.html.fromstring(response.data)
        form = html.forms[0]

        invitation_hex = form.fields['invitation_hex']

        self.assertEqual(InvitationData.invitation.hex, invitation_hex)
        email = form.fields['email']

        self.assertEqual(InvitationData.invitation.email_lower, email)

        response = self.client.post(url_for('auth.sign_up'), data={
            'invitation_hex': invitation_hex,
            'username': 'Boris',
            'email': email,
            'password': 'password',
            'password_again': 'password'
        })
        self.assertRedirects(response, url_for('root.home'))
        self.assertAuthenticated()

        try:
            user = auth_service.user_by_username_or_email(InvitationData.invitation.email_lower)
        except NoResultFound:
            self.fail('User not created.')

        self.assertEquals('Boris', user.username)
        self.assertEquals('boris', user.username_lower)
        self.assertEquals(InvitationData.invitation.email_lower, user.email_lower)
        self.assertTrue(user.check_password('password'))
        self.assertTrue(user.active)

        try:
            profile = profiles_service.profile(user.id)
            self.assertEqual(InvitationData.invitation.email_lower, profile.email)
        except NoResultFound:
            self.fail('Profile not created.')

        invitations = models_service.invitations_by_email(email)
        self.assertFalse(invitations)

        roles = models_service.user_roles(user.id)
        self.assertEqual(1, len(roles))
        role = roles[0]
        self.assertEqual(InvitationData.invitation.model_id, role.model_id)
        self.assertEqual(InvitationData.invitation.role, role.role)


    @fixtures(UserData, ProfileData)
    def test_login(self, data):
        response = self.client.post(url_for('auth.login'), data={
            'username_or_email': UserData.first.username,
            'password': 'password'
        })
        self.assertRedirects(response, url_for('root.home'))
        self.assertAuthenticated()

        self.logout()

        response = self.client.post(url_for('auth.login'), data={
            'username_or_email': ProfileData.first.email,
            'password': 'password'
        })
        self.assertRedirects(response, url_for('root.home'))
        self.assertAuthenticated()

        self.logout()

        response = self.client.post(url_for('auth.login') + '?next=' + url_for('root.secure'), data={
            'username_or_email': ProfileData.first.email,
            'password': 'password',
        })
        self.assertRedirects(response, url_for('root.secure'))
        self.assertAuthenticated()

    @fixtures(UserData)
    def test_logout(self, data):
        self.login(UserData.first)

        response = self.client.get(url_for('auth.logout'))
        self.assertRedirects(response, url_for('root.home'))
        self.assertNotAuthenticated()







