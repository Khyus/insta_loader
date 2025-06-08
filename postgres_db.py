import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    state = Column(String, nullable=False)

engine = create_engine('postgresql://myuser:mypassword@localhost/moses_db')
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = SessionFactory()

class UserManager:
    def __init__(self, session):
        self.session = session

    def add_user(self, username, state):
        user = User(username=username, state=state)
        self.session.add(user)
        self.session.commit()
        print(f'Added user {username} with ID {user.id}')
        return user.id

    def get_user(self, id):
        return self.session.query(User).filter_by(id).one()

    def update_user_state(self, user_id, state):
        user = self.get_user(user_id)
        if user:
            user.state = state
            self.session.commit()
            print(f'Update user {user_id} to state {state}')
        else:
            print(f'User {user_id} not found')

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            print(f'Deleted user {user_id}')


