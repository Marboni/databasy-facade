from datetime import timedelta, datetime
from functools import wraps
from flask import url_for
from flask.ext.testing import TestCase
import os
import time
from databasyfacade import app, db
from databasyfacade.db import dbs
from databasyfacade.mq.engine import rpc_server, pub_server

__author__ = 'Marboni'

class DatabasyTest(TestCase):
    def create_app(self):
        os.environ.setdefault('DATABASY_ENV', 'testing')
        return app.create_app()

    def setUp(self):
        db.recreate_db(self.app.config['DATABASE_URI'])

    def tearDown(self):
        dbs().rollback()
        rpc_server().unbind()
        pub_server().unbind()

    @property
    def mail(self):
        from databasyfacade.utils.mail_sender import mail
        return mail

    def wait_letter(self, outbox, expected_letters_count, timeout):
        timeout_time = datetime.now() + timedelta(seconds=timeout)
        while datetime.now() < timeout_time:
            letters_in_outbox = len(outbox)
            if letters_in_outbox == expected_letters_count:
                return
            if letters_in_outbox > expected_letters_count:
                self.fail('%s letter(s) expected, %s received.' % (expected_letters_count, letters_in_outbox))
            time.sleep(0.05)
        self.fail('%s letter(s) didn\'t received during %s seconds.' % (expected_letters_count, timeout))


    def login(self, test_user):
        self.client.post(url_for('auth.login'), data={
            'email': test_user.email_lower,
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
    from databasyfacade.testing.testdata import fixture
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
