from operator import or_
from flask import url_for, current_app
from databasyfacade.db import dbs
from databasyfacade.db.auth import User, Profile
from databasyfacade.utils import tokens

__author__ = 'Marboni'

def send_activation_mail(profile):
    token = tokens.create_token(tokens.EMAIL_CONFIRMATION_TOKEN_TYPE, profile.user_id)
    callback_url = current_app.config['ENDPOINT'] + url_for('auth.activate').rstrip('/')
    confirmation_link = '%s/?token=%s' % (callback_url, token.hex)
    profile.send_mail_async('Registration Confirmation', 'mails/activation.txt', confirmation_link=confirmation_link)

def send_password_reset_mail(profile):
    token = tokens.create_token(tokens.PASSWORD_RESET_TOKEN_TYPE, profile.user_id, expires_in=48)
    callback_url = current_app.config['ENDPOINT'] + url_for('auth.change_password').rstrip('/')
    reset_password_link = '%s/?token=%s' % (callback_url, token.hex)
    profile.send_mail_async('Reset Password', 'mails/password_reset.txt', user_name=profile.user.username, reset_password_link=reset_password_link)

def create_user(username, email, raw_password, active):
    """ Creates user and his profile. Send letter with email activation token. Newly-created user is not active.
    Returns:
        profile of the new user.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    """
    user = User()
    user.set_username(username)
    user.set_password(raw_password)
    user.active = active

    profile = Profile()
    profile.user = user
    profile.set_email(email)

    dbs().add(user)
    dbs().add(profile)
    dbs().flush()

    return profile

def activate_user(token_hex):
    """ Check email confirmation token and make account active if token is valid.
    Returns:
        user if token is valid and account activated, None otherwise.
    """
    token = tokens.retrieve_token(token_hex, tokens.EMAIL_CONFIRMATION_TOKEN_TYPE)
    if not token:
        return None
    else:
        tokens.delete_token(token_hex)
        user = user_by_id(token.user_id)
        user.active = True
        return user

def reset_password(token, new_password):
    """ Changes user's password using token.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    Returns:
        user with the new password.
    """
    user = change_password(token.user_id, new_password)
    tokens.delete_token(token.hex, tokens.PASSWORD_RESET_TOKEN_TYPE)
    return user

def change_password(user_id, new_password):
    """ Changes user's password.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    Returns:
        user with the new password.
    """
    user = user_by_id(user_id)
    user.set_password(new_password)
    dbs().flush()
    return user

def username_exists(username):
    """ Returns if user with specified username exists.
    Returns:
        True if user exists, False otherwise.
    """
    return bool(dbs().query(User).filter_by(username_lower=username.lower()).count())

def email_exists(email):
    """ Returns if user with specified email exists.
    Returns:
        True if user exists, False otherwise.
    """
    return bool(dbs().query(User).filter_by(email_lower=email.lower()).count())

def user_by_id(user_id):
    """ Retrieves user by ID.
    Returns:
        user.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    """
    return dbs().query(User).filter_by(id=user_id).one()

def user_by_username_or_email(username_or_email):
    """ Retrieves user by username or email.
    Returns:
        user.
    Raises:
        NoResultFound if user with this username or email doesn't exist.
    """
    value_lower = username_or_email.lower()
    return dbs().query(User).filter(or_(User.email_lower==value_lower, User.username_lower==value_lower)).one()

def users_by_email(emails):
    """ Retrieves users with emails specified in list.
    Returns:
        users with emails specified in list, so number of users will be <= number of emails in list.
    """
    emails = (email.lower() for email in emails)
    return dbs().query(User).filter(User.email_lower.in_(emails)).all()