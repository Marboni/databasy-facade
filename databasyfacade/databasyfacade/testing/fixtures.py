from pbkdf2 import crypt
from sqlalchemy import create_engine
from databasyfacade import config
import uuid
from fixture import DataSet, SQLAlchemyFixture, NamedDataStyle

__author__ = 'Marboni'

CONFIG = config.config_by_mode('testing')

TEST_DB_URI = CONFIG.DATABASE_URI
PASSWORD = crypt('password', CONFIG.SECRET_KEY)

def uuid_hex():
    return uuid.uuid4().hex


fixture = SQLAlchemyFixture(
    env=globals(),
    style=NamedDataStyle(),
    engine=create_engine(TEST_DB_URI)
)

#noinspection PyUnresolvedReferences
from databasyfacade.db.auth import User   # Need to import it to give NamedDataStyle an opportunity to map it.
class UserData(DataSet):
    class hero:
        id = 1001L
        name = 'Hero'
        email = 'Hero@databasy.com'
        email_lower = 'hero@databasy.com'
        password = PASSWORD
        active = True


