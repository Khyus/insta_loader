import time
import random
from datetime import datetime
import instaloader
import pandas as pd
from sqlalchemy import Column, Integer, text, String, ForeignKey, Table, create_engine, Boolean, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

from create_db import Reels, User, init_db

Base = declarative_base()
loader = instaloader.Instaloader()

reels_session = init_db('reels_db')
general_session = init_db('general')

def insert_reels(owner, reels_id, has_audio, video_url, video_view_count, caption,
                 comment_count, timestamp, likes_count, location, pinned, product_type):


    timestamp = datetime.fromtimestamp(timestamp).isoformat()
    try:
        reel = Reels(owner=owner, reels_id=reels_id, has_audio=has_audio, video_url=video_url,
                     video_view_count=video_view_count,
                     caption=caption, comment_count=comment_count, timestamp=timestamp, likes_count=likes_count['count'],
                     location=location,product_type=product_type)

        reels_session.add(reel)
        reels_session.commit()
        update_db_state(owner['username'], 'completed_reels')
        print('here...')
        print(f"{time.ctime()}-db_size:{len(reels_session.query(Reels).all())}({owner['username']})", end='\r')

    except IntegrityError:
        reels_session.rollback()

def update_db_state(user, state):
    try:
        general_session.execute(text(f'''
                                        UPDATE users
                                        SET state = '{state}'
                                        WHERE username = '{user}';
                                        '''))
        general_session.commit()
    except Exception as e:
        print(f'error: {e}')
        general_session.rollback()

def get_username():
    user_list = [u[0] for u in general_session.execute(text('''
            SELECT username 
            FROM users
            WHERE state = 'progressing';
    ''')).fetchall()]
    user = random.choice(user_list)
    return user

for i in range(25):
    try:
        user = get_username()
        print(user)
        response = loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={user}', params={})
        update_db_state(user, 'in_progress')
        for edge in response['data']['user']['edge_owner_to_timeline_media']['edges']:
            node = edge['node']
            if node['is_video']:
                insert_reels(node['owner'],node['id'],node['has_audio'],node['video_url'],node['video_view_count'],node['edge_media_to_caption'],
                             node['edge_media_to_comment'],node['taken_at_timestamp'],node['edge_liked_by'],node['location'],node['pinned_for_users'],node['product_type'])
        update_db_state(user, 'completed')
    except Exception as e:
        print(f'error: {e}')
        break
