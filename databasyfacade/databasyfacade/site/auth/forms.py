from flask.ext.wtf import Form
import re
from sqlalchemy.orm.exc import NoResultFound
from wtforms import TextField, validators, PasswordField, ValidationError, HiddenField, BooleanField
from wtforms.validators import Required
from databasyfacade.services import auth_service

__author__ = 'Marboni'

class SignUpForm(Form):
    invitation_hex = HiddenField('Invitation HEX', id='su_invitation_hex')

    username = TextField('Username', [
        validators.Length(min=3, max=15)
    ], id='su_username')

    email = TextField('Email', [validators.Email()], id='su_email')

    password = PasswordField('Password', [
        validators.Length(min=6, max=30),
        validators.EqualTo('password_again', message='Passwords don\'t match.')
    ], id='su_password')

    password_again = PasswordField('Password again', id='su_password_again')

    def validate_username(self, field):
        if not re.match('^[\w\-]+$', field.data):
            raise ValidationError('Username may only contain latin letters, digits, underscore and hyphen symbols.')
        if auth_service.username_exists(field.data):
            raise ValidationError('This username is already taken.')

    def validate_email(self, field):
        if auth_service.email_exists(field.data):
            raise ValidationError('This email is already registered.')


class LoginForm(Form):
    next = HiddenField('Next', id='li_next')
    username_or_email = TextField('Username or email', [Required()], id='li_username_or_email')
    password = PasswordField('Password', [Required()], id='li_password')
    remember_me = BooleanField('Remember me', default=True, id='li_remember_me')


class ResetPasswordForm(Form):
    email = TextField('Email', [validators.Email()], id='pr_email')


class ChangePasswordForm(Form):
    token = HiddenField('Token', id='pc_token')

    old_password = PasswordField('Old password', id='pc_password')

    new_password = PasswordField('New password', [
        validators.Length(min=6, max=30),
        validators.EqualTo('new_password_again', message='Passwords don\'t match.')
    ], id='pc_new_password')

    new_password_again = PasswordField('New password again', id='pc_new_password_again')

    def validate_old_password(self, field):
        token = self.token.data
        old_password = field.data

        if not token and not old_password:
            raise ValidationError('This field is required.')