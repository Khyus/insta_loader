import time
import random
from datetime import datetime
import instaloader
import pandas as pd
from sqlalchemy import Column, Integer, text, String, ForeignKey, Table, create_engine, Boolean, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

from create_db import Media, User, init_db

Base = declarative_base()
loader = instaloader.Instaloader()

general_session = init_db('general')

def insert_media(owner_id, owner, url, caption,
                 comment_count, timestamp, likes_count, location, media_type,
                 has_audio = None, views=None):


    timestamp = datetime.fromtimestamp(timestamp).isoformat()
    try:
        media = Media(owner_id=owner_id, owner=owner, has_audio=has_audio, url=url,
                     views = views, caption=caption, comment_count=comment_count, timestamp=timestamp, likes_count=likes_count,
                     location=location,media_type=media_type)
        print(f'{media_type}:{media.media_type}')

        general_session.add(media)
        general_session.commit()
        update_db_state(owner, 'completed_reels')
        print(f"db_size:{len(general_session.query(Media).all())}", end='\r')

    except IntegrityError:
        print(f'{media.media_type} not added.')
        general_session.rollback()
#
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
            WHERE state = 'empty';
    ''')).fetchall()]
    user = random.choice(user_list)
    return user

for i in range(1):
    #try:
    user = get_username()
    print(user)
    response = loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={user}', params={})
    #update_db_state(user, 'in_progress')
    for edge in response['data']['user']['edge_owner_to_timeline_media']['edges']:
        node = edge['node']
        if node['is_video']:
            insert_media(owner_id=node['owner']['id'], owner= node['owner']['username'],has_audio = node['has_audio'],
                         url = node['video_url'], views = node['video_view_count'],caption = node['edge_media_to_caption'],
                         comment_count= node['edge_media_to_comment'],timestamp=node['taken_at_timestamp'],likes_count=node['edge_liked_by']['count'],
                         location=node['location'],media_type='reels')
        elif node.get('edge_sidecar_to_children', False):
            insert_media(owner_id=node['owner']['id'], owner=node['owner']['username'],url=node['edge_sidecar_to_children'],
                         caption=node['edge_media_to_caption'],comment_count=node['edge_media_to_comment'],timestamp=node['taken_at_timestamp'],
                         likes_count=node['edge_liked_by']['count'], location=node['location'],media_type='carousel')
        elif node.get('id', None):
            insert_media(owner_id=node['owner']['id'], owner=node['owner']['username'], url=node['display_url'],
                         caption=node['edge_media_to_caption'], comment_count=node['edge_media_to_comment'],timestamp=node['taken_at_timestamp'],
                         likes_count=node['edge_liked_by']['count'], location=node['location'],media_type='photo')

    #update_db_state(user, 'completed')
    # except Exception as e:
    #     print(f'error: {e}')
    #     break
