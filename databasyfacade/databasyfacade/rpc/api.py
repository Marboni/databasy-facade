from functools import wraps
from flask.ext.login import UserMixin
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade import db
from databasyfacade.services import profiles_service, models_service

__author__ = 'Marboni'

def touch_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            db.remove_session()

    return wrapper


def echo(msg):
    return msg

@touch_db
def user_info(user_id):
    try:
        profile = profiles_service.profile(user_id)
        return {
            'user_id': profile.user.id,
            'name': profile.name,
            'email': profile.email,
            'active': profile.user.active
        }
    except NoResultFound:
        return None

@touch_db
def database_type(model_id):
    try:
        model = models_service.model(model_id)
        return model.database_type
    except NoResultFound:
        return None