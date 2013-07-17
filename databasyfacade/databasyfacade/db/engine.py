from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__author__ = 'Marboni'

Base = declarative_base()
engine = None
Session = None
dbs = lambda: Session()

def init_engine(uri, **kwargs):
    global engine
    global Session
    engine = create_engine(uri, **kwargs)
    sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Session = scoped_session(sm)
    return engine

def remove_session():
    Session.remove()

def recreate_db(uri):
    engine = create_engine(uri, echo=False)

    # We need to update it when new module appears. It's error-prone, need to be done automatically.
    from databasyfacade.db import auth, models

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
