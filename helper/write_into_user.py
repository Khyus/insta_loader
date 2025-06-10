import time
import random
from create_db import Media, User, init_db
import instaloader


loader = instaloader.Instaloader()
session = init_db('general')

def update_db(session, username, bio, is_private, is_professional_account, is_business_account,
              business_address, category_name, category_enum, media_size):
    if not bio:
        bio = 'empty'
    session.query(User).filter_by(username=username).update({
        'bio':bio,
        'is_private':is_private,
        'is_professional_account': is_professional_account,
        'is_business_account': is_business_account,
        'business_address':business_address,
        'category_name': category_name,
        'category_enum': category_enum,
        'media_size':media_size
    })
    session.commit()

def get_username(session):
    #username = session.execute(get_user_query).fetchone()[0]
    users = [u[0] for u in session.query(User.username).filter_by(state='empty').all()]
    username = random.choice(users)
    session.query(User).filter_by(username=username).update({
        'state':'in_progress'
    })
    session.commit()
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
    media_size = data['data']['user']['edge_owner_to_timeline_media']['count']

    return bio, is_private, is_professional_account, is_business_account, business_address, category_name, category_enum, media_size

while True:
#for _ in range(2):
    try:
        username = get_username(session)
        print(f'{time.ctime()} processing {username}....')
        #bio, is_private = get_profile_data(username)
        update_db(session, username, *get_profile_data(username))
    except:
        print(f'{time.ctime()} brokedown..')
