from sqlalchemy import Column, Integer, text, String, DateTime, ForeignKey, Table, create_engine, Boolean, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy import Column, Integer, text, String, DateTime, ForeignKey, Table, create_engine, Boolean, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

Base = declarative_base()

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer)  # owner['id']
    owner = Column(String)      # owner['username']
    has_audio = Column(Boolean)    # only for reels
    url = Column(JSON, nullable=False)   # depending on media type
    views = Column(Integer, nullable=False)    # only for reels
    caption = Column(JSON)          # edge_media_to_caption
    comment_count = Column(JSON)    # edge_media_to_comment
    timestamp = Column(DateTime)
    likes_count = Column(Integer)
    location = Column(JSON)
    media_type = Column(String)

    def __repr__(self):
        return f"<Media(url='{self.url}')>"



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
    is_private = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_professional_account = Column(Boolean)
    is_business_account = Column(Boolean)
    business_address = Column(String)
    category_name = Column(String)
    category_enum = Column(String)
    media_size = Column(Integer)

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