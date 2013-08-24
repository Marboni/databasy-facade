from pbkdf2 import crypt
from sqlalchemy import create_engine
from databasyfacade import config
import uuid
from fixture import DataSet, SQLAlchemyFixture, NamedDataStyle
from databasyfacade.db import models
from databasyfacade.utils import tokens

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
from databasyfacade.db.auth import User
class UserData(DataSet):
    class first:
        id = 1001L
        email_lower = 'first@databasy.com'
        password = PASSWORD
        active = True

    class second:
        id = 1002L
        email_lower = 'second@databasy.com'
        password = PASSWORD
        active = True

    class third:
        id = 1003L
        email_lower = 'third@databasy.com'
        password = PASSWORD
        active = True


#noinspection PyUnresolvedReferences
from databasyfacade.db.auth import Profile
class ProfileData(DataSet):
    class first:
        id = 1001L
        user_id = UserData.first.id
        name = 'Mr. First'
        email = 'First@databasy.com'

    class second:
        id = 1002L
        user_id = UserData.second.id
        name = 'Mr. Second'
        email = 'Second@databasy.com'

    class third:
        id = 1003L
        user_id = UserData.third.id
        name = 'Mr. Third'
        email = 'Third@databasy.com'

#noinspection PyUnresolvedReferences
from databasyfacade.db.models import ModelInfo
class ModelInfoData(DataSet):
    class model_a:
        id = 1001L
        schema_name = 'ModelA'
        description = 'ModelA Schema'
        database_type = models.DB_TYPES[0][0]

    class model_b:
        id = 1002L
        schema_name = 'ModelB'
        description = 'ModelB Schema'
        database_type = models.DB_TYPES[0][0]

from databasyfacade.db.models import ModelRole
class ModelRoleData(DataSet):
    class first_owner_model_a:
        id = 1001L
        model_id = ModelInfoData.model_a.id
        user_id = UserData.first.id
        role = ModelRole.OWNER

    class first_developer_model_b:
        id = 1002L
        model_id = ModelInfoData.model_b.id
        user_id = UserData.first.id
        role = ModelRole.DEVELOPER

    class second_owner_model_b:
        id = 1003L
        model_id = ModelInfoData.model_b.id
        user_id = UserData.second.id
        role = ModelRole.OWNER

#noinspection PyUnresolvedReferences
from databasyfacade.db.models import Invitation
class InvitationData(DataSet):
    class invitation:
        id = 1001L
        model_id = ModelInfoData.model_b.id
        email_lower = 'invited@databasy.com'
        hex = tokens.generate_hex()
        role = ModelRole.DEVELOPER
        active = True

    class inactive_invitation:
        id = 1002L
        model_id = ModelInfoData.model_b.id
        email_lower = 'invited_inactive@databasy.com'
        hex = tokens.generate_hex()
        role = ModelRole.DEVELOPER
        active = False


