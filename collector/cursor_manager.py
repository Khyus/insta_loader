from datetime import datetime
import logging
from typing import Optional
from sqlalchemy import Column, String, DateTime, create_engine, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

FOLLOWING_HASH = '58712303d941c6855d4e888c5f0cd22f'
FOLLOWER_HASH  = '37479f2b8209594dde7facb0d904896a'

Base = declarative_base()


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
cursor_logger = logging.getLogger('cursor')
cursor_logger.setLevel(logging.DEBUG)
logger_handler = logging.FileHandler('cursor.log')
logger_handler.setFormatter(formatter)
cursor_logger.addHandler(logger_handler)


class Cursor(Base):
    __tablename__ = 'cursor'
    id = Column(Integer(), default=1, primary_key=True)
    lastfetch = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    cursor = Column(String(), default=None)

    def __repr__(self):
        return f'Cursor(lastfetch={self.lastfetch}, cursor={self.cursor})'.format(self=self)

def init_db(db_path='sqlite:///cursor.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session()

session = init_db('sqlite:///cursor.db')


def update_cursor(new_cursor: Optional[str] = None):
    # cursor = session.query(Cursor).filter_by(id=1).first()
    # if not cursor:
    #     session.add(Cursor())
    #     session.commit()
    #     cursor = session.query(Cursor).filter_by(id=1).first()
    cursor = _get_cursor_object()
    cursor.cursor = new_cursor
    session.commit()
    cursor_logger.info(f'new_cursor: {new_cursor}')

def _get_cursor_object():
    cursor = session.query(Cursor).filter_by(id=1).first()
    if not cursor:
        session.add(Cursor())
        session.commit()
        cursor = session.query(Cursor).filter_by(id=1).first()
    return cursor

def get_cursor():
    cursor = _get_cursor_object()
    return cursor.cursor

def fetch_following(loader, user_name, user_id):
    cursor = get_cursor()
    data = loader.context.graphql_query(FOLLOWING_HASH,
                                        {'id': str(user_id), 'first': 50,
                                         'after': cursor},
                                        'https://www.instagram.com/{0}/'.format(user_name))['data']['user']['edge_follow']

    # private account (not accessable)
    if not data['edges'] and data['count'] > 0:
        update_cursor(None)
        return [], False

    new_cursor = data['page_info']['end_cursor']
    has_next_page = data['page_info']['has_next_page']
    #user_list = [d['node']['username'] for d in data['edges']]
    user_list = [d['node'] for d in data['edges']]

    if has_next_page:
        update_cursor(new_cursor)
    else:
        update_cursor(None)

    return user_list, has_next_page

def fetch_follower(loader, user_name, user_id):
    cursor = get_cursor()
    data = loader.context.graphql_query(FOLLOWER_HASH,
                                        {'id': str(user_id), 'first': 50,
                                         'after': cursor},
                                        'https://www.instagram.com/{0}/'.format(user_name))['data']['user']['edge_followed_by']


    # private account (not accessable)
    if not data['edges'] and data['count'] > 0:
        update_cursor(None)
        return [], False


    new_cursor = data['page_info']['end_cursor']
    has_next_page = data['page_info']['has_next_page']
    #user_list = [d['node']['username'] for d in data['edges']]
    user_list = [d['node'] for d in data['edges']]

    if has_next_page:
        update_cursor(new_cursor)
    else:
        update_cursor(None)

    return user_list, has_next_page



# loader.context.graphql_query(FOLLOWING_HASH,
#                                         {'id': str('314216'), 'first': 5,
#                                          'after': None},
#                                         'https://www.instagram.com/{0}/'.format('zuck'))