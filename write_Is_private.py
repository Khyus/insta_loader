import time
import asyncio
import instaloader
from db import init_db, User

session = init_db('sqlite:///moses.db')
count = 0


async def worker(username):
    loader = instaloader.Instaloader()
    data = loader.context.get_iphone_json(f'api/v1/users/web_profile_info/?username={username}',params={})
    print(f"{time.ctime()} worker: {username} - {data['data']['user']['is_private']}")

def chunk_generator(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

async def run():
    user_list = [u[0] for u in session.query(User.username).all()]
    for chunk in chunk_generator(user_list, 74):
        workers = [worker(c) for c in chunk]
        await asyncio.gather(*workers)

asyncio.run(run())
