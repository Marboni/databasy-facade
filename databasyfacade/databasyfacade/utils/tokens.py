import time
from uuid import uuid4
import datetime
import re
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.db import dbs
from databasyfacade.db.auth import Token

__author__ = 'Marboni'

TOKEN_HEX_REGEXP = re.compile(r'[0-9a-f]{32}')

EMAIL_CONFIRMATION_TOKEN_TYPE = 'email_confirmation'
AUTH_TOKEN_TYPE = 'auth'
PASSWORD_RESET_TOKEN_TYPE = 'password_reset'

def create_token(type, user_id=None, params=None, expires_in=None):
    """ Creates token.
    Returns:
        newly-created token.
    """
    if user_id and not str(user_id).isdigit():
        raise ValueError('User ID must be positive integer, not %s.' % user_id)
    if params and not isinstance(params, dict):
        raise ValueError('Data must be a dict, not %s.' % type(params))
    if not params:
        params = {}
    hex = uuid4().hex
    if expires_in:
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=expires_in)
        expires = time.mktime(expiration_time.timetuple())
    else:
        expires = None
    token = Token()
    token.hex = hex
    token.type = type
    token.user_id = user_id
    token.params = params
    token.expires = expires
    dbs().add(token)
    dbs().flush()
    return token


def retrieve_token(hex, type=None, user_id=None):
    """ Retrieves token.
    Returns:
        token or None if token not found.
    """
    if not TOKEN_HEX_REGEXP.search(hex):
        return None
    now = time.mktime(time.localtime())
    try:
        criterion = [
            Token.hex == hex,
            or_(Token.expires == None, Token.expires > now)
        ]
        if type:
            criterion.append(
                Token.type == type
            )
        if user_id:
            criterion.append(
                Token.user_id == user_id
            )
        return dbs().query(Token).filter(*criterion).one()
    except NoResultFound:
        return None

def user_tokens(user_id):
    return dbs().query(Token).filter_by(user_id=user_id).all()

def delete_token(hex, type=None):
    """ Deletes token.
    Returns:
        True if token has been found and deleted, False otherwise.
"""
    ft = {'hex': hex}
    if type:
        ft['type'] = type
    return dbs().query(Token).filter_by(**ft).delete()
