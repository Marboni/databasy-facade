from databasyfacade import db
from databasyfacade.services import profiles_service

__author__ = 'Marboni'

def echo(msg):
    return msg

def profile(user_id):
    profile = profiles_service.profile(user_id)
    db.remove_session()
    return profile
