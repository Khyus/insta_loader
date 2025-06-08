import asyncio
import json
from db import User, init_db, add_user,db_size
from haralyzer import HarParser

from async_system_v2 import FollowingSystem, FollowerSystem


# user_session = init_db('moses_db')
#
# system = FollowingSystem(user_session = user_session)
# asyncio.run(system.run())

########################################################################################
user_session = init_db('visitalburywodonga')
system = FollowerSystem(user_session=user_session, user_name='visitalburywodonga',user_id='527977347')
asyncio.run(system.run())
########################################################################################


##############################################################################################
# user_session = init_db('madamwheels')
#
# def count_likers(file_path):
#     with open(file_path,'r',encoding='utf-8') as f:
#         har_parser = HarParser(json.loads(f.read()))
#     har_data = har_parser.har_data
#     return har_data
#
# count = []
# entries = count_likers('./madamwheels.har')['entries']
# for entry in entries:
#     data = json.loads(entry['response']['content']['text'])['users']
#     for user in data:
#         count.append(user['id'])
#         #print(d['id'],d['username'],d['is_verified'])
#         # add_user(session = user_session, username=user['username'], user_id=user['id'],original_followers=True, is_verified=user['is_verified'])
#         # print(f'db_size: {db_size(user_session)}', end='\r')
#
#################################################################################################
