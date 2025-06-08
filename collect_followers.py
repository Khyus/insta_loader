from db import User, init_db


user_session = init_db('sqlite:///moses.db')









users = user_session.query(User).all()

for user in users:
    if user.original_followers == True:
        if user.state == 'in_progress':
            # start from there.
        elif user.state == 'empty':
            continue

