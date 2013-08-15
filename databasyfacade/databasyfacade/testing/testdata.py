from pbkdf2 import crypt
from sqlalchemy import create_engine
from databasyfacade import config
import uuid
from fixture import DataSet, SQLAlchemyFixture, NamedDataStyle
from databasyfacade.db import models

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
        email_lower = 'hero@databasy.com'
        password = PASSWORD
        active = True


#noinspection PyUnresolvedReferences
from databasyfacade.db.auth import Profile   # Need to import it to give NamedDataStyle an opportunity to map it.
class ProfileData(DataSet):
    class hero:
        id = 1001L
        user_id = UserData.hero.id
        name = 'Hero'
        email = 'Hero@databasy.com'


#noinspection PyUnresolvedReferences
from databasyfacade.db.models import ModelInfo   # Need to import it to give NamedDataStyle an opportunity to map it.
class ModelInfoData(DataSet):
    class psql:
        id = 1001L
        schema_name = 'Postgres'
        description = 'PostgreSQL Schema'
        database_type = models.DB_TYPES[0][0]
        owner_id = UserData.hero.id