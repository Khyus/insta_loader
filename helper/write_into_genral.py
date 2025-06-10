import time
import random
import instaloader
import pandas as pd
from create_db import init_db, User, Media
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


query = text('''
SELECT user_id, username, bio, is_private, is_verified, is_professional_account, is_business_account, business_address, category_name, category_enum
FROM users;
''')


session = init_db('general')
# what do we do

class UpdateDB:
    def __init__(self, db_name, csv_path):
        self.session = init_db(db_name)
        self.df = pd.read_csv(csv_path)
        #self.run()

    def add_user(self,username: str, user_id: str,bio: str = None, is_private: bool = False,
                 is_verified: bool = False):
        try:
            user = User(username=username,user_id = user_id, is_private=is_private, is_verified=is_verified)
            self.session.add(user)
            self.session.commit()

        except IntegrityError:
            self.session.rollback()

    def db_size(self):
        return len(self.session.query(User).all())


    def change_user_state(self,username, state):
        user = self.session.query(User).filter_by(username=username).first()
        user.state = state
        self.session.commit()

    def add_to_db(self, row):
        self.add_user(row['username'], row['user_id'], row['is_private'], row['is_verified'])
        print(self.db_size(), end='\r')

    def run(self):
        self.df.apply(lambda row: self.add_to_db(row), axis=1)
#df = pd.read_csv()

csv_path = '/home/tilaemia/Documents/interior_design_data.csv'
update = UpdateDB('general', csv_path=csv_path)

