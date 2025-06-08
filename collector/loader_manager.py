import pickle
import json
from os import WCONTINUED
from typing import Optional

from ldap3.strategy.reusable import TERMINATE_REUSABLE
from sqlalchemy import Column, Integer, String, create_engine, LargeBinary, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

import instaloader

Base = declarative_base()

class Insta_Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    passwd = Column(String, nullable=False)
    session_data = Column(JSON, nullable=True, default=None)


    def __repr__(self):
        return f'Insta_Session(user_name={self.user_name})'.format(self=self)

def init_db(db_path = 'sqlite:///loaders.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

session = init_db()

def add_session(session, user_name: str, passwd: str):
    loader = instaloader.Instaloader()
    print(f'logging in {user_name}....')

    loader.login(user_name, passwd)
    session_data = loader.save_session()

    insta_session = Insta_Session(user_name=user_name, passwd=passwd, session_data=session_data)
    try:
        print(f'saving {user_name}....')
        session.add(insta_session)
        session.commit()
    except IntegrityError:
        session.rollback()

# not ready...
def reload_session(session, user_name, passwd):
    insta_session = session.query(Insta_Session).filter_by(user_name=user_name).first()
    loader = instaloader.Instaloader()
    loader.login(user_name, passwd)
    print(f'logged in..')
    session_data = loader.save_session()

    insta_session.session_data = session_data
    session.commit()
    return insta_session

def list_all_sessions(session):
    details = session.query(Insta_Session).all()
    return details

def get_loaders(session):
    insta_sessions = session.query(Insta_Session).all()
    loaders = []
    for s in insta_sessions:
        loader = instaloader.Instaloader()
        loader.load_session(s.user_name, s.session_data)
        loaders.append(loader)

    return loaders



def get_loader(session, user_name: str):
    insta_session = session.query(Insta_Session).filter_by(user_name=user_name).first()
    loader = instaloader.Instaloader()
    loader.load_session(insta_session.user_name, insta_session.session_data)

    return loader

# original plan.
def status(session):
    for insta_session in session.query(Insta_Session).all():
        loader = get_loader(insta_session.user_name)
        try:
            data = loader.context.graphql_query("d6f4427fbe92d846298cf93df0b937d3", {})["data"]["user"]
            if data:
                insta_session.is_logged_in = True
                session.commit()
        except:
            insta_session.is_logged_in = False
            session.commit()

# original plan.
def get_ready_loaders(session):
    loaders = []
    for insta_session in session.query(Insta_Session).all():
        loader = get_loader(session, insta_session.user_name)
        try:
            data = loader.context.graphql_query("d6f4427fbe92d846298cf93df0b937d3", {})["data"]["user"]
            if data:
                loaders.append(loader)
        except:
            print(f'{insta_session.user_name} failed!!')
            pass
    return loaders

















#
# def log_all(db_session):
#     log_details = db_session.query(Loaders).all()
#     for user, passwd in log_details:
#         loader = login(user, passwd)
#         log_details.loader = loader
#         db_session.commit()
#
#     - log_status
#
#     - relog-all()
#
#     - relog()
#     - add_log()