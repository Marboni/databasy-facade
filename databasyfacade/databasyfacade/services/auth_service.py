from flask import url_for, current_app
from databasyfacade.db import dbs
from databasyfacade.db.auth import User, Profile
from databasyfacade.utils import tokens

__author__ = 'Marboni'

def send_activation_mail(user):
    token = tokens.create_token(tokens.EMAIL_CONFIRMATION_TOKEN_TYPE, user.id)
    callback_url = current_app.config['ENDPOINT'] + url_for('auth.activate').rstrip('/')
    confirmation_link = '%s/?token=%s' % (callback_url, token.hex)
    user.send_mail('Registration Confirmation', 'mails/activation.txt', confirmation_link=confirmation_link)

def create_user(name, email, raw_password, active):
    """ Creates user and his profile. Send letter with email activation token. Newly-created user is not active.
    Returns:
        new user.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    """
    user = User()
    user.name = name
    user.set_email(email)
    user.set_password(raw_password)
    user.active = active
    dbs().add(user)
    dbs().flush()

    profile = Profile()
    profile.user = user
    dbs().add(profile)
    dbs().flush()

    return user

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

def email_exists(email):
    """ Returns if user with specified email exists.
    Returns:
        True if user exists, False otherwise.
    """
    return bool(dbs().query(User).filter_by(email_lower=email.lower()).count())

def user_by_id(userid):
    """ Retrieves user by ID.
    Returns:
        user.
    Raises:
        NoResultFound if user with this ID doesn't exist.
    """
    return dbs().query(User).filter_by(id=userid).one()

def user_by_email(email):
    """ Retrieves user by email.
    Returns:
        user.
    Raises:
        NoResultFound if user with this email doesn't exist.
    """
    return dbs().query(User).filter_by(email_lower=email.lower()).one()
