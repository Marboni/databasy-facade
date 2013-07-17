from databasyfacade.db import dbs
from databasyfacade.db.auth import Profile, User

__author__ = 'Marboni'

def profile(user_id):
    """ Retrieves user's profile.
    Returns:
        profile.
    Raises:
        NoResultFound if profile not found.
    """
    return dbs().query(Profile).join(Profile.user).filter(User.id == user_id).one()
