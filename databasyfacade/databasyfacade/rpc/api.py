from functools import wraps
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
def profile(user_id):
    return profiles_service.profile(user_id)

@touch_db
def database_type(model_id):
    model = models_service.model(model_id)
    return model.database_type