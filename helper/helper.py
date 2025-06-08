import time
import random
import instaloader

import pandas as pd
from sqlalchemy import Column, Integer, text, String, ForeignKey, Table, create_engine, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

query = text('''
SELECT user_id, username, bio, is_private, is_verified, is_professional_account, is_business_account, business_address, category_name, category_enum
FROM users;
''')

Base = declarative_base()


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


    def __repr__(self):
        return f"<User(username='{self.username}')>"

def init_db(db_name: str):
    db_path = f'postgresql://insta:mypassword@localhost/{db_name}'
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

session = init_db('general')

def create_df(name: str):
    data = session.execute(query).fetchall()

    df = pd.DataFrame(data=data,
                      columns=['user_id', 'username', 'bio', 'is_private', 'is_verified', 'is_professional_account',
                               'is_business_account', 'business_address', 'category_name', 'category_enum'])
    df['url'] = 'https://www.instagram.com/' + df['username'] + '/'

    df.to_csv(name + '.csv')
    return df


class Enrish:
    def __init__(self, db_name: str = 'general'):
        self.session = init_db(db_name)
        self.loader = instaloader.Instaloader()


    def get_username(self):
        # username = session.execute(get_user_query).fetchone()[0]
        users = self.session.query(User).filter_by(bio=None).all()
        username = users[random.randint(0, len(users))].username
        # self.session.query(User).filter_by(username=username).update({
        #     'bio': 'in_progress'
        # })
        return username

    def get_profile_data(self, username):
        data = self.loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={username}', params={})
        bio = str(data['data']['user']['biography'])
        is_private = data['data']['user']['is_private']
        is_professional_account = data['data']['user']['is_professional_account']
        is_business_account = data['data']['user']['is_business_account']
        business_address = data['data']['user']['business_address_json']
        category_name = data['data']['user']['category_name']
        category_enum = data['data']['user']['category_enum']

        return bio, is_private, is_professional_account, is_business_account, business_address, category_name, category_enum

    def update_db(self, username, bio, is_private, is_professional_account, is_business_account,
                  business_address, category_name, category_enum):
        if not bio:
            bio = 'empty'
        self.session.query(User).filter_by(username=username).update({
            'bio': bio,
            'is_private': is_private,
            'is_professional_account': is_professional_account,
            'is_business_account': is_business_account,
            'business_address': business_address,
            'category_name': category_name,
            'category_enum': category_enum
        })
        self.session.commit()

    def run(self):
        while True:
            try:
                username = self.get_username()
                print(f'{time.ctime()} processing {username}....')

                # bio, is_private = get_profile_data(username)

                self.update_db(username, *self.get_profile_data(username))
                print(f'{time.ctime()} updated {username}')
            except:
                print(f'{time.ctime()} breakdown..')

csv_path = '/home/tilaemia/Documents/advancing/basics/beyond_the_basics/NLP/Text Analysis May/horse_data.csv'
enrish = Enrish()
