from uuid import uuid4
from flask import current_app
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import String, BigInteger, Enum, Boolean
from databasyfacade.db import Base
from databasyfacade.db.auth import User

__author__ = 'Marboni'

DB_TYPES = [
    ('postgres.models.PostgresModel', 'PostgreSQL')
]

class ModelInfo(Base):
    __tablename__ = 'model_info'


    DATABASE_TYPE_ENUM = Enum(
        *(db_type_and_name[0] for db_type_and_name in DB_TYPES),
        name='DATABASE_TYPE'
    )

    id = Column(BigInteger, primary_key=True)
    schema_name = Column(String(128), nullable=False)
    description = Column(String(1024))
    database_type = Column(DATABASE_TYPE_ENUM, nullable=False)
    repo_server = Column(String(32), nullable=False)
    owner_id = Column(BigInteger, ForeignKey('usr.id'))
    owner = relationship(User, backref=backref("models", cascade='all'))

    def full_path(self):
        return 'http://%s.%s/models/%s' % (self.repo_server, current_app.config['DOMAIN'], self.id)

    def __repr__(self):
        return "<Model('%s')>" % self.name

class ModelRole(Base):
    __tablename__ = 'model_role'

    __table_args__ = (
        Index('ix_model_role_model_info_id_user_id', 'model_info_id', 'user_id'),
        )

    ADMIN = 'admin'
    DEVELOPER = 'developer'
    VIEWER = 'viewer'

    HIERARCHY = {
        ADMIN: [DEVELOPER, VIEWER],
        DEVELOPER: [VIEWER]
    }

    ROLES = [
        ADMIN,
        DEVELOPER,
        VIEWER
    ]

    MODEL_ROLE_ENUM = Enum(ADMIN, DEVELOPER, VIEWER, name='MODEL_ROLE')

    id = Column(BigInteger, primary_key=True)
    model_info_id = Column(BigInteger, ForeignKey('model_info.id', ondelete='CASCADE'))
    model = relationship(ModelInfo, backref=backref("model_roles", cascade='all', passive_deletes=True))
    user_id = Column(BigInteger, ForeignKey('usr.id'))
    user = relationship(User, backref=backref("model_roles", cascade='all'))
    role = Column(MODEL_ROLE_ENUM, nullable=False)

    def includes(self, role):
        return self.role == role or role in (ModelRole.HIERARCHY.get(self.role) or [])

class Invitation(Base):
    __tablename__ = 'invitation'

    __table_args__ = (
        Index('ix_invitation_email_lower_active', 'email_lower', 'active'),
        )

    id = Column(BigInteger, primary_key=True)
    email_lower = Column(String(50), nullable=False)
    # account_id = NULL and active = False if account was removed.
    model_info_id = Column(BigInteger, ForeignKey('model_info.id'), nullable=True, index=True)
    model_info = relationship(ModelInfo, backref=backref('invitations'))
    role = Column(ModelRole.MODEL_ROLE_ENUM, nullable=False)
    hex = Column(String(32), unique=True)
    active = Column(Boolean, default=True)

    def __init__(self, model_id=None, email=None, role=None):
        self.hex = uuid4().hex
        self.model_id = model_id
        self.email_lower = email.lower() if email else None
        self.role = role