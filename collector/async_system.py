import asyncio
import time
import random
import instaloader

from loader_manager import get_loaders, get_ready_loaders
import loader_manager
from cursor_manager import fetch_follower
from db import User, add_user, db_size, init_db

class FollowerSystem:
    def __init__(self, user_session, user_name, user_id):
        self.user_session = user_session
        self.user_name = user_name
        self.user_id = user_id
        self.stop = asyncio.Event()
        self.main_lock = asyncio.Lock()
        self.print_lock = asyncio.Lock()

    async def main_task(self, loader, user_name, user_id):
        async with self.main_lock:
            if self.stop.is_set():
                return None, None, []
            print(f'{time.ctime()} {loader.context.username} working..')
            try:
                user_list, has_next_fetch = fetch_follower(loader, user_name, user_id)
            except Exception as e:
                user_list = [], has_next_fetch=True
                print(f'{time.ctime()}-{loader.context.username} encounterd error: {e}')
            print(f'{time.ctime()}-{loader.context.username} collected!')
            if not has_next_fetch:
                print(f'{time.ctime()} End of page!')
                self.stop.set()
                return None, True, user_list

            return time.time(), True, user_list

    async def print_task(self, user_list, loader):
        print(f'{time.ctime()}-{loader.context.username} writing to db..')
        for user in user_list:
            add_user(session = self.user_session, username=user['username'], user_id=user['id'],original_followers=True, is_verified=user['is_verified'])
            print(f'db_size: {db_size(self.user_session)}', end='\r')

    async def worker(self, loader, user_name, user_id):
        while True:
            if self.stop.is_set():
                print('first stop breaking.....')
                break

            main_end, collected, user_list = await self.main_task(loader, user_name, user_id)
            print(f'{time.ctime()}-{loader.context.username} just collected {len(user_list)} usernames')
            await self.print_task(user_list=user_list, loader=loader)
            print(f'{time.ctime()}-{loader.context.username} wrote to db successfully!')



            if self.stop.is_set():
                break

            now = time.time()
            if main_end is None:
                main_end = 0
            remaining_delay = max(0, (30 - (now - main_end)))
            await asyncio.sleep(remaining_delay)
            print(f'{time.ctime()}-{loader.context.username}..DONE resting.')

    async def run(self):
        loader_session = loader_manager.init_db('sqlite:///loaders.db')
        loaders = get_ready_loaders(loader_session)
        self.stop.clear()
        workers = [self.worker(loader, self.user_name, self.user_id) for loader in loaders]
        await asyncio.gather(*workers)

        print(f'{time.ctime()} system stopped' if self.stop.is_set()
              else f'{time.ctime()} All task completed.')
        print(f'db_size: {db_size(self.user_session)}', end='\r')

# user_session = init_db('rgenteel_ng')
# system = FollowerSystem(user_session=user_session, user_name='rgenteel.ng',user_id='40593757685')
# asyncio.run(system.run())

