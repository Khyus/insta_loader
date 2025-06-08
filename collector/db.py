import threading

from sqlalchemy import Column, Integer, text, String, ForeignKey, Table, create_engine, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tests')
logger.setLevel(logging.DEBUG)
logger_handler = logging.FileHandler('info.log')
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)


Base = declarative_base()



follows = Table(
    'follows',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'),primary_key=True),
    Column('following_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    user_id = Column(String, unique=True, nullable=False)
    state = Column(String, default='empty')
    bio = Column(String)
    original_followers = Column(Boolean, default=False, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_professional_account = Column(Boolean)
    is_business_account = Column(Boolean)
    business_address = Column(String)
    category_name = Column(String)
    category_enum = Column(String)

    following = relationship(
        'User',
        secondary=follows,
        primaryjoin='User.id == follows.c.follower_id',
        secondaryjoin='User.id == follows.c.following_id',
        backref='followers'
    )

    def __repr__(self):
        return f"<User(username='{self.username}')>"

def init_db(db_name: str):
    db_path = f'postgresql://insta:mypassword@localhost/{db_name}'
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# def init_db(db_path: str = 'postgresql://insta:mypassword@localhost/moses_db'):
#     engine = create_engine(db_path)
#     Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     return Session()

#session = init_db()


def add_user(session, username: str, user_id: str,bio: str = None, original_followers: bool = False, is_private: bool = False,
             is_verified: bool = False):
    try:
        user = User(username=username,user_id = user_id, bio=bio, original_followers=original_followers,
                    is_private=is_private, is_verified=is_verified)
        session.add(user)
        session.commit()
        logger.info(f'Threading: {threading.currentThread().name} - plus one ({username})')

    except IntegrityError:
        session.rollback()
        logger.info(f'Threading: {threading.currentThread().name} - minus one ({username})')

def db_size(session):
    return len(session.query(User).all())


def change_user_state(session, username, state):
    user = session.query(User).filter_by(username=username).first()
    user.state = state
    session.commit()


def add_followings(session ,username: str, following_username: str,following_id: str, is_verified: str):

    user = session.query(User).filter_by(username=username).first()

    follow = session.query(User).filter_by(username=following_username).first()
    if not follow:
        follow = User(username=following_username,user_id = following_id, original_followers=False,is_verified=False, is_private=False)
    try:
        user.following.append(follow)
    except IntegrityError:
        session.rollback()

def show_following_table(session):
    query = text("""
    SELECT u2.username AS followings, u1.username AS follower_username
    FROM users u1
    JOIN follows f ON u1.id = f.follower_id
    JOIN users u2 ON u2.id = f.following_id
    ORDER BY u2.username, u1.username
    """)
    return session.execute(query).fetchall()





