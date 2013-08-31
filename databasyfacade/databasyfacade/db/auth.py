from flask.ext.login import UserMixin

__author__ = 'Marboni'

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import String, Integer, Boolean, BigInteger
from flask import current_app, json
from databasyfacade.db.engine import Base
from pbkdf2 import crypt

__author__ = 'Marboni'

class User(Base, UserMixin):
    __tablename__ = 'usr'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(15), unique=True, nullable=False)
    username_lower = Column(String(15), unique=True, nullable=False)
    email_lower = Column(String(50), unique=True, nullable=False)
    password = Column(String(80))
    active = Column(Boolean())

    def set_username(self, username):
        self.username = username
        self.username_lower = username.lower()

    def set_password(self, raw_password):
        self.password = crypt(raw_password, current_app.config['SECRET_KEY'])

    def check_password(self, raw_password):
        return self.password == crypt(raw_password, current_app.config['SECRET_KEY'])

    def is_active(self):
        return self.active

    def __repr__(self):
        return "<User('%s')>" % self.email_lower


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('usr.id', ondelete='CASCADE'), unique=True)
    user = relationship('User', backref=backref('profile', uselist=False))

    email = Column(String(50), unique=True, nullable=False)

    def set_email(self, email):
        self.email = email
        self.user.email_lower = email.lower()

    def send_mail(self, subject, template, **kwargs):
        kwargs['username'] = self.user.username
        from databasyfacade.utils import mail_sender
        mail_sender.send(self.email, subject, template, **kwargs)

    def send_mail_async(self, subject, template, **kwargs):
        kwargs['username'] = self.user.username
        from databasyfacade.utils import mail_sender
        mail_sender.send_async(self.email, subject, template, **kwargs)

class Token(Base):
    __tablename__ = 'token'

    __table_args__ = (
        Index('ix_token_hex_expires', 'hex', 'expires'),
        )

    id = Column(BigInteger, primary_key=True)
    hex = Column(String(32))
    type = Column(String(32))
    user_id = Column(BigInteger)
    params_json = Column(String(1024), nullable=True)
    expires = Column(Integer, nullable=True, index=True)

    @property
    def params(self):
        return json.loads(self.params_json)

    @params.setter
    def params(self, params):
        self.params_json = json.dumps(params)
