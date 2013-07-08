from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField, ValidationError, HiddenField, BooleanField
from databasyfacade.services import auth_service

__author__ = 'Marboni'

class SignUpForm(Form):
    name = TextField('Your name', [
        validators.Length(min=1, max=40)
    ], id='su_name')

    email = TextField('Email', [validators.Email()], id='su_email')

    password = PasswordField('Password', [
        validators.Length(min=6, max=30),
        validators.EqualTo('password_again', message='Passwords don\'t match.')
    ], id='su_password')

    password_again = PasswordField('Password again', id='su_password_again')


    def validate_email(self, field):
        if auth_service.email_exists(field.data):
            raise ValidationError('This email is already registered.')


class LoginForm(Form):
    next = HiddenField('Next', id='li_next')

    email = TextField('Email', [
        validators.Email()
    ], id='li_email')

    password = PasswordField('Password', id='li_password')

    remember_me = BooleanField('Remember me', default=True, id='li_remember_me')



