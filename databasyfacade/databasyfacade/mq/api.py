from functools import wraps
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade import db
from databasyfacade.db import dbs
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
            'username': profile.user.username,
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


@touch_db
def delete_model(model_id):
    model = models_service.delete_model(model_id)
    dbs().commit()
    return {
        'schema_name': model.schema_name,
        'description': model.description,
        'database_type': model.database_type
    }


@touch_db
def delete_role(model_id, user_id):
    models_service.delete_role(model_id, user_id)
    dbs().commit()


@touch_db
def role(model_id, user_id):
    try:
        r = models_service.role(model_id, user_id)
    except NoResultFound:
        return None
    return r.role