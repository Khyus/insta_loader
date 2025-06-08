import instaloader
import threading
import logging
import time
import random
from db import add_user, init_db, User

FOLLOWING_HASH = '58712303d941c6855d4e888c5f0cd22f'
FOLLOWER_HASH = '37479f2b8209594dde7facb0d904896a'

OPAY_ID = '13472554034'
OPAY_USERNAME = 'opay.ng'

LIST_OF_CURSORS = ['QVFCZWJwQ3RSQTlFRXhJSVRkbU9QTEZldTFGMFh6UHVPbDlxU2tLaE1LZ0xJbUJoMlZJVm1udTVOVWVheTZYTHQ1NW9NWW91aDQtelhxekpNRTBUc2ZrQg==',
                   'QVFDejQ0OEZMcFJKQlN0eGxLN1VtcnA4M283aFNKbkk1ZkxCVkxZWmlCTEZjMVYzcUU5UnVxaUZ6akxZU2JkdnN4WkZLS0FWZzZtRGFBUExBRXh5SllDZQ==',
                   'QVFBVHVBRFRGcS0zN2lpd3p0UlEzcHFVckRoTXNhNk05enhRbXNRX0pWaGgwQmVuaWcxRkpyM3RMTXdfVEI1MFVGdTBSQkZ0Q1YwVnJRMnFoRXBlOWFQMA==',
                   'QVFEOFVhTnFLNFFqb1VkZ3dqaDdaY3NhZW43WnJkeHk4SjN0ZlIyYkNOUUowTHpmdXpoVGtOYVhYbkxTVEZ4Nzh2Qy1fUTY0S0RrY3RfZWExa0J2MWt4dA==',
                   'QVFDbHRybHA0N0Z2NjZhYXJ5NXEtTlZpbjIzeGttZEJTMFpRWURVcENvQThpSTNzSEFyUkd2WGFvNkRaM0Q5LXFTbFZWYU16QlEzLThkMGlpeW5hSlNPTg==',
                   'QVFCWWRJM05UMFVoUkVld3l4UnN6djBCUUF1OWlPc1pRNC1MRGxjYW5SWURheVJtX0pJOFBlZDJyUDNKcU4wQ2tmQUphNHk1R2JSaENweUVKQUg4ZFdmRg==']

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        #logging.StreamHandler(),
        logging.FileHandler('crash.log')
    ]
)
logger = logging.getLogger(__name__)

loader = instaloader.Instaloader()

def login(user, passwd):
    loader = instaloader.Instaloader()
    loader.login(user, passwd)
    return loader


session = init_db('sqlite:///paritiehub.db')
lock = threading.Lock()


def collect_following(account_id: int, account_name : str, cursor: str):
    return loader.context.graphql_query( FOLLOWING_HASH,
                                 {'id': str(OPAY_ID), 'first': 12,
                                'after': cursor},
                                 'https://www.instagram.com/{0}/'.format(OPAY_USERNAME))

def collect_follower(account_id: str, account_name : str, cursor: str):
    data = loader.context.graphql_query( FOLLOWER_HASH,
                                 {'id': account_id, 'first': 12,
                                'after': cursor},
                                 'https://www.instagram.com/{0}/'.format(account_name))['data']['user']['edge_followed_by']

    user_list = [d['node']['username'] for d in data['edges']]
    end_cursor = data['page_info']['end_cursor']

    for u in user_list:
        add_user(session, u,' ', is_private=False, is_verified=False)

    return user_list, end_cursor


#######################
def test_collect_follower(loader, account_id: str, account_name: str, cursor: str):
    session = init_db('sqlite:///paritiehub.db')
    index = 0

    has_next_page = True


    try:
        while has_next_page == True:
            try:
                data = loader.context.graphql_query(FOLLOWER_HASH,
                                                    {'id': str(account_id),'first': 50,
                                                     'after': cursor},
                                                    'https://www.instagram.com/{0}/'.format(account_name))['data']['user']['edge_followed_by']
            except:
                print(f'Thread: {threading.current_thread().name} crashed: last cursor {cursor} (except)')

            count = data['count']

            has_next_page = data['page_info']['has_next_page']
            user_list = [d['node']['username'] for d in data['edges']]

            with lock:
                for u in user_list:
                    index += 1
                    add_user(session, u, ' ', is_private=False, is_verified=False)

            if has_next_page:
                cursor = data['page_info']['end_cursor']

            print(f'{index}/{count}', end='\r')
            #logger.info(f'Thread: {threading.current_thread().name}, has_more: {has_next_page} \n cursor: {cursor} ')
            rest_time = random.randint(8, 9)
            #logger.info(f'{threading.current_thread().name}, waiting {rest_time}......')
            time.sleep(rest_time)
    finally:
        print(f'Thread: {threading.current_thread().name} crashed: last cursor {cursor} (finally)')
        session.close()


# loader_1 = login('khay_us', 'A42#4pc7')
# loader_2 = login('jones_action', 'actionlady123456')
# loader_3 = login('fadhilatize', 'fadh2005')
# loader_4 = login('she_smiles33','fadh2005')
# loader_5 = login('sagelennow','A42#4pc7')
# loader_6 = login('writersgenii','A42#4pc7')
# loader_7 = login(khairatcollections2023','Khairat4')


#
#
# t1 = threading.Thread(target=test_collect_follower, args=(loader_1, '45409388909','lashinteriorsdesign',LIST_OF_CURSORS[0]), name='Thread-1')
# t2 = threading.Thread(target=test_collect_follower, args=(loader_2, '2040191930','dustedwoodworking',LIST_OF_CURSORS[2]), name='Thread-2')
# t3 = threading.Thread(target=test_collect_follower, args=(loader_3,'2040191930','dustedwoodworking',LIST_OF_CURSORS[-1]), name='Thread-3')
#
# data = loader.context.graphql_query(FOLLOWER_HASH,
#                                                     {'id': str('314216'),'first': 5,
#                                                      'after': None},
#                                                     'https://www.instagram.com/{0}/'.format('zuck'))['data']['user']['edge_followed_by']


loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={self.username}',
                                                         params={})