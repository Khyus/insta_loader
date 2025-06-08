import asyncio
import time
import random

from sqlalchemy.exc import IntegrityError


import instaloader
import loader_manager
from loader_manager import get_loaders, init_db, get_ready_loaders
from cursor_manager import fetch_follower, fetch_following
from db import User, add_user, db_size, add_followings, change_user_state
from db_iterable import DB_iterator, DB_iterable

class FollowingSystem:
    def __init__(self, user_session):
        self.user_session = user_session
        self.stop = asyncio.Event()
        self.main_lock = asyncio.Lock()
        self.print_lock = asyncio.Lock()
        self.followers_user_list = iter(DB_iterable(self.user_session))
        self.user = None
        self.next_user()

    def next_user(self):
        while True:
            try:
                user = self.followers_user_list.next_user()
                if user.original_followers:
                    # if user.state == 'in_progress':
                    #     self.user = user
                    #     break
                    if user.state == 'empty':
                        self.user = user
                        break

            except StopIteration:
                print(f'{self.user_session} COMPLETED!')
                break
    #
    # def initilize_db(self):
    #     return init_db(self.db_path)

    async def main_task(self, loader):
        async with self.main_lock:

            # End of loop...exit
            if self.stop.is_set():
                return None, None, []

            print(f'{time.ctime()} {loader.context.username} working..')
            try:
                user_list, has_next_fetch = fetch_following(loader=loader, user_name= self.user.username, user_id= self.user.user_id)
            except Exception as e:
                user_list = [], has_next_fetch = True
                print(f'{time.ctime()}-{loader.context.name} encountered error: {e}')
            print(f'{time.ctime()} {loader.context.username} collected...')

            if not has_next_fetch:
                print(f'{time.ctime()}-{self.user.username}-End of page!')
                #with self.print_lock:
                change_user_state(self.user_session, self.user.username, 'completed')
                # self.stop.set()
                try:
                    self.next_user()
                    print(f'{time.ctime()} processing {self.user}...')
                except StopIteration:
                    self.stop.set() # Exit all
                return None, True, user_list

            return time.time(), True, user_list

    async def print_task(self,user_list, loader):
        #async with self.print_lock:
        print(f'{time.ctime()} locked by {loader.context.username}')
        change_user_state(self.user_session, self.user.username, 'in_progress')
        for user in user_list:
            try:
                add_followings(self.user_session, username= self.user.username,following_username=user['username'], following_id=user['id'], is_verified=user['is_verified'])
                print(f'db_size: {db_size(self.user_session)}', end='\r')
            except IntegrityError:
                self.user_session.rollback()
        print(f'{time.ctime()} locked released by {loader.context.username}')

    async def worker(self, loader):
        while True:
            if self.stop.is_set():  # Exits all workers.
                break
            try:
                main_end, collected, user_list = await self.main_task(loader=loader)
            except Exception as e:
                print(f'{time.ctime()}-{loader} FAILED: {e}')
            print(f'{time.ctime()}-{loader.context.username} just collected {len(user_list)} usernames')
            await self.print_task(user_list=user_list, loader=loader)
            print(f'{time.ctime()}-{loader.context.username} wrote to database successfully.')

            # if main_end is not None:
            #     await self.print_task(user_list=user_list)
            # elif main_end is None and collected:
            #     if self.stop.is_set():
            #         await self.print_task(user_list=user_list)
            #         break

            if self.stop.is_set():
                break

            #if not main_end:
            now = time.time()
            if main_end is None:
                main_end = 0
            remaining_delay = max(0, (30 - (now - main_end)))
            await asyncio.sleep(remaining_delay)
            print(f'{time.ctime()}-{loader.context.username}..DONE resting.')

    async def run(self):
        loader_session = init_db('sqlite:///loaders.db')
        loaders = get_ready_loaders(loader_session)

        print(f'Processing...{self.user}')
        self.stop.clear()
        workers = [self.worker(loader=loader) for loader in loaders]
        await asyncio.gather(*workers)

        print(f'{time.ctime()} system stopped' if self.stop.is_set()
              else f'{time.ctime()} {self.user} completed.')
        print(f'db_size: {db_size(self.user_session)}', end='\r')
#
# system = FollowingSystem()
# asyncio.run(system.run())


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
        loader_session = loader_manager.init_db('sqlite:///loadersV2.db')
        loaders = get_ready_loaders(loader_session)
        self.stop.clear()
        print(len(loaders))
        workers = [self.worker(loader, self.user_name, self.user_id) for loader in loaders]
        await asyncio.gather(*workers)

        print(f'{time.ctime()} system stopped' if self.stop.is_set()
              else f'{time.ctime()} All task completed.')
        print(f'db_size: {db_size(self.user_session)}', end='\r')

# user_session = init_db('rgenteel_ng')
# system = FollowerSystem(user_session=user_session, user_name='rgenteel.ng',user_id='40593757685')
# asyncio.run(system.run())





