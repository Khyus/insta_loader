import asyncio
import time
import random
import instaloader

from loader_manager import get_loaders, init_db, get_ready_loaders
from cursor_manager import fetch_follower
from db import User, add_user, db_size

class WorkerSystem:
    def __init__(self):
        self.stop = asyncio.Event()
        self.main_lock = asyncio.Lock()
        self.print_lock = asyncio.Lock()

    async def main_task(self, loader, user_name, user_id):
        async with self.main_lock:
            if self.stop.is_set():
                return None, None, []
            print(f'{time.ctime()} {loader.context.username} working..')
            user_list, has_next_fetch = fetch_follower(loader, user_name, user_id)

            if not has_next_fetch:
                print(f'{time.ctime()} End of page!')
                self.stop.set()
                return None, True, user_list

            return time.time(), True, user_list

    async def print_task(self, user_list):
        async with self.print_lock:
            for user in user_list:
                add_user(username=user['username'], user_id=user['id'],original_followers=True, is_verified=user['is_verified'])
                print(f'db_size: {db_size()}', end='\r')

    async def worker(self, loader, user_name, user_id):
        while True:
            if self.stop.is_set():
                print('first stop breaking.....')
                break

            main_end, collected, user_list = await self.main_task(loader, user_name, user_id)
            # if main_end is not None or (main_end is None and collected):
            #     await self.print_task(user_list)
            if main_end is not None:
                await self.print_task(user_list)
            elif main_end is None and collected:
                if self.stop.is_set():
                    await self.print_task(user_list)
                    break


            if self.stop.is_set():
                break

            now = time.time()
            remaining_delay = max(0, (30 - (now - main_end)))
            await asyncio.sleep(remaining_delay)

    async def run(self):
        loader_session = init_db('sqlite:///loaders.db')
        loaders = get_ready_loaders(loader_session)
        self.stop.clear()
        workers = [self.worker(loader, 'paritiefied', '48370384064') for loader in loaders]
        await asyncio.gather(*workers)
        print(f'{time.ctime()} system stopped' if self.stop.is_set()
              else f'{time.ctime()} All task completed.')
        print(f'db_size: {db_size()}', end='\r')


system = WorkerSystem()
asyncio.run(system.run())

