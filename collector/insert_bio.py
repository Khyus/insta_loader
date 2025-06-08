import time
import random
import instaloader
from db import init_db, User
from sqlalchemy import text


loader = instaloader.Instaloader()
session = init_db('general')


get_user_query = text('''
SELECT username
FROM users
WHERE original_followers = True and bio = ''
ORDER BY id
''')




def update_db(session, username, bio, is_private, is_professional_account, is_business_account,
              business_address, category_name, category_enum):
    if not bio:
        bio = 'empty'
    session.query(User).filter_by(username=username).update({
        'bio':bio,
        'is_private':is_private,
        'is_professional_account': is_professional_account,
        'is_business_account': is_business_account,
        'business_address':business_address,
        'category_name': category_name,
        'category_enum': category_enum
    })
    session.commit()

def get_username(session):
    #username = session.execute(get_user_query).fetchone()[0]
    users = session.query(User).filter_by(original_followers=True).filter_by(bio=None).all()
    username = users[random.randint(0, len(users))].username
    session.query(User).filter_by(username=username).update({
        'bio':'in_progress'
    })
    return username

def get_profile_data(username):
    data = loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={username}', params={})
    bio = str(data['data']['user']['biography'])
    is_private = data['data']['user']['is_private']
    is_professional_account = data['data']['user']['is_professional_account']
    is_business_account = data['data']['user']['is_business_account']
    business_address = data['data']['user']['business_address_json']
    category_name = data['data']['user']['category_name']
    category_enum = data['data']['user']['category_enum']

    return bio, is_private, is_professional_account, is_business_account, business_address, category_name, category_enum

while True:
    try:
        username = get_username(session)
        print(f'{time.ctime()} processing {username}....')

        #bio, is_private = get_profile_data(username)

        update_db(session, username, *get_profile_data(username))
        print(f'{time.ctime()} updated {username}')
    except:
        print(f'{time.ctime()} brokedown..')


#print(f"{time.ctime()}-{len([q[0] for q in session.query(User.bio).all() if q[0] is not None])}")


#corpus = []
# for data in data_path:
#     for d in data['node']['edge_media_to_caption']['edges']:
#         corpus.append(d['node']['text'])