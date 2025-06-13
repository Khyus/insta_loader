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

    def add_user(self,row):
        params = {
            'username': None if pd.isna(row['username']) else row['username'],
            'user_id': None if pd.isna(row['user_id']) else row['user_id'],
            'state': None if pd.isna(row['state']) else row['state'],
            'bio': None if pd.isna(row['bio']) else row['bio'],
            'is_private': None if pd.isna(row['is_private']) else row['is_private'],
            'is_verified': None if pd.isna(row['is_verified']) else row['is_verified'],
            'is_professional_account': None if pd.isna(row['is_professional_account']) else row['is_professional_account'],
            'is_business_account': None if pd.isna(row['is_business_account']) else row['is_business_account'],
            'business_address': None if pd.isna(row['business_address']) else row['business_address'],
            'category_name': None if pd.isna(row['category_name']) else row['category_name'],
            'category_enum': None if pd.isna(row['category_enum']) else row['category_enum'],
            'media_size': None if pd.isna(row['media_size']) else row['media_size']
        }
        try:

            user = User(username=params['username'], user_id=params['user_id'],state=params['state'],bio=params['bio'],
                        is_private=params['is_private'],is_verified=params['is_verified'],
                        is_professional_account = params['is_professional_account'], is_business_account=params['is_business_account'],
                        business_address=params['business_address'],category_name=params['category_name'],category_enum=params['category_enum'],
                        media_size=params['media_size'])
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
        self.add_user(row)
        print(self.db_size(), end='\r')

    def run(self):
        self.df.iloc[:,3:].apply(lambda row: self.add_to_db(row), axis=1)
#df = pd.read_csv()

csv_path = "/home/tilaemia/Documents/shared_space/NLP/leather_users.csv"
update = UpdateDB('general', csv_path=csv_path)

