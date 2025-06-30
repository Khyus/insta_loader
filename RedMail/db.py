import pandas as pd

from sqlalchemy import String, Column, Integer, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class Emails(Base):
    __tablename__ = 'emails'
    id = Column(Integer,primary_key=True)
    url = Column(String)
    username = Column(String)
    email = Column(String)
    priority = Column(String)
    status = Column(String)

    def __repr__(self):
        return f"<Emails(url='{self.username}')>"

def init_db(db_name: str):
    db_path = f'postgresql://postgres:mypassword@localhost/{db_name}'
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def add_email(url, username, email, priority):
    try:
        new_email = Emails(url=url, username=username, email=email, priority=priority)
        session.add(new_email)
        session.commit()
        print(len(session.query(Emails).all()), end='\r')

    except IntegrityError:
        session.rollback()


class Write_To_DB:
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def run(self):
        self.csv_file.apply(lambda row: add_email(row['url'],row['usernames'],row['email'],row['Priority']), axis=1)

csv_file = pd.read_csv('/home/tilaemia/Downloads/leather_emails.csv')
session = init_db('email')
update_email = Write_To_DB(csv_file)







