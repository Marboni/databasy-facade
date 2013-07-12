from functools import wraps
from flask import url_for
from flask.ext.testing import TestCase
import os
from databasyfacade import app, db
from databasyfacade.db import dbs

__author__ = 'Marboni'

class DatabasyTest(TestCase):
    def create_app(self):
        os.environ.setdefault('DATABASY_ENV', 'testing')
        return app.create_app()

    def setUp(self):
        db.recreate_db(self.app.config['DATABASE_URI'])

    def tearDown(self):
        dbs().rollback()

    @property
    def mail(self):
        from databasyfacade.utils.mail_sender import mail

        return mail

    def login(self, test_user):
        self.client.post(url_for('auth.login'), data={
            'email': test_user.email,
            'password': 'password'
        })
        if not self.is_authenticated():
            raise Exception('Unable to login user')

    def logout(self):
        self.client.get(url_for('auth.logout'))
        if self.is_authenticated():
            raise Exception('Unable to logout user')

    def is_authenticated(self):
        return self.client.get(url_for('root.secure')).status_code == 200

    def assertAuthenticated(self):
        if not self.is_authenticated():
            self.fail('User is not authenticated.')

    def assertNotAuthenticated(self):
        if self.is_authenticated():
            self.fail('User is authenticated.')

def fixtures(*datasets):
    from databasyfacade.testing.fixtures import fixture
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            data = fixture.data(*datasets)
            data.setup()
            kwargs['data'] = data
            try:
                function(*args, **kwargs)
            finally:
                data.teardown()
        return wrapper

    return decorator
