from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = 'Marboni'

Session = sessionmaker()

def init_db(url, echo):
    engine = create_engine(url, echo)
    Session.configure(bind=engine)

