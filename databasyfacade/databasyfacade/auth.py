from databasyfacade.db import dbs
from databasyfacade.db.auth import User

__author__ = 'Marboni'

def load_user(user_id):
    return dbs().query(User).get(user_id)
