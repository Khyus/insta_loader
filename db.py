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

list_logger = logging.getLogger('lists')
list_logger.setLevel(logging.INFO)
list_handler = logging.FileHandler('list_info.log')
list_handler.setFormatter(formatter)
list_logger.addHandler(list_handler)

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
    is_private = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    following = relationship(
        'User',
        secondary=follows,
        primaryjoin='User.id == follows.c.follower_id',
        secondaryjoin='User.id == follows.c.following_id',
        backref='followers'
    )

    def __repr__(self):
        return f"<User(username='{self.username}')>"

def init_db(db_path: str = 'postgresql://insta:mypassword@localhost/moses_db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

session = init_db()


def add_user(username: str, user_id: str,bio: str = None, original_followers: bool = False, is_private: bool = False,
             is_verified: bool = False):
    try:
        user = User(username=username,user_id = user_id, bio=bio, original_followers=original_followers,
                    is_private=is_private, is_verified=is_verified)
        session.add(user)
        session.commit()
        logger.info(f'Threading: {threading.currentThread().name} - plus one ({username})')

    except IntegrityError:
        logger.info(f'Threading: {threading.currentThread().name} - minus one ({username})')

def db_size():
    return len(session.query(User).all())


def add_followings(username: str, following_username: str, bio: str,is_private: str, is_verified: str):
    user = session.query(User).filter_by(username=username).first()

    follow = session.query(User).filter_by(username=following_username).first()
    if not follow:
        follow = User(username=following_username,bio=bio,original_followers=False,
                      is_private=is_private, is_verified=False)
    user.following.append(follow)

def show_following_table(session):
    query = text("""
    SELECT u2.username AS followings, u1.username AS follower_username
    FROM users u1
    JOIN follows f ON u1.id = f.follower_id
    JOIN users u2 ON u2.id = f.following_id
    ORDER BY u2.username, u1.username
    """)
    return session.execute(query).fetchall()

def get_response():
    loaded_data = []
    with open('data.txt', 'r') as f:
        for line in f:
            # Split the line and convert elements to appropriate types
            parts = line.strip().split(',')
            loaded_data.append((parts[0], int(parts[1]), parts[2]))

    print(loaded_data)
    return loaded_data




