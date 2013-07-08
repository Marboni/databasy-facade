from databasyfacade.db import dbs
from databasyfacade.db.auth import Profile

__author__ = 'Marboni'

def profile(user_id):
    """ Retrieves user's profile.
    Returns:
        profile.
    Raises:
        NoResultFound if profile not found.
    """
    return dbs().query(Profile).filter_by(user_id=user_id).one()
