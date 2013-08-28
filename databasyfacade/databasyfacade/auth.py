from functools import wraps
from flask import request
from flask.ext.login import current_user
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import Unauthorized
from databasyfacade.db import dbs
from databasyfacade.db.auth import User
from databasyfacade.services import models_service

__author__ = 'Marboni'

def load_user(user_id):
    return dbs().query(User).get(user_id)


def has_role(role):
    """ Checks if user has required role for a model.
        Model ID will be taken from request field or url part with name "model_id".
    Parameters:
        role - required role.
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            values = dict(request.values.items() + kwargs.items())
            try:
                model_id = values['model_id']
            except KeyError:
                raise ValueError('model_id not found in request parameters.')
            if not check_role(model_id, role):
                raise Unauthorized
            return function(*args, **kwargs)

        return wrapper

    return decorator

def check_role(model_id, role):
    user = current_user
    if not user.is_authenticated():
        return False
    try:
        user_role = models_service.role(model_id, user.id)
    except NoResultFound:
        return False
    return user_role.includes(role)