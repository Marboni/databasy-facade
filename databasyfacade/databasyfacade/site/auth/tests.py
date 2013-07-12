from flask import url_for
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.services import auth_service, profiles_service
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.fixtures import UserData
from databasyfacade.utils import tokens

__author__ = 'Marboni'

class AuthTest(DatabasyTest):
    def test_sign_up_and_activate(self):
        with self.mail.record_messages() as outbox:
            response = self.client.post('/', data={
                'name': 'Boris',
                'email': 'BMarchenko@databasy.com',
                'password': 'password',
                'password_again': 'password'
            })
            self.assert200(response)
            self.assertTrue('BMarchenko@databasy.com' in response.data)

            try:
                user = auth_service.user_by_email('bMarchenko@databasy.com')
            except NoResultFound:
                self.fail('User not created.')

            self.assertEqual('bmarchenko@databasy.com', user.email_lower)
            self.assertTrue(user.check_password('password'))
            self.assertFalse(user.active)

            try:
                profile = profiles_service.profile(user.id)
                self.assertEqual('Boris', profile.name)
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

            response = self.client.get(activation_link)
            self.assertRedirects(response, url_for('root.home'))
            self.assertAuthenticated()


    @fixtures(UserData)
    def test_login(self, data):
        response = self.client.post(url_for('auth.login'), data={
            'email': UserData.hero.email,
            'password': 'password'
        })
        self.assertRedirects(response, url_for('root.home'))
        self.assertAuthenticated()

        self.logout()

        response = self.client.post(url_for('auth.login') + '?next=' + url_for('root.secure'), data={
            'email': UserData.hero.email,
            'password': 'password',
        })
        self.assertRedirects(response, url_for('root.secure'))
        self.assertAuthenticated()

    @fixtures(UserData)
    def test_logout(self, data):
        self.login(UserData.hero)

        response = self.client.get(url_for('auth.logout'))
        self.assertRedirects(response, url_for('root.home'))
        self.assertNotAuthenticated()







