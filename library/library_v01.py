import asyncio
import time
import random

class WorkerSystem:
    def __init__(self):
        self.stop = asyncio.Event()
        self.main_lock = asyncio.Lock()
        self.print_lock = asyncio.Lock()
        self.print_tasks = []


    async def main_task(self, worker_id, i):
        async with self.main_lock:
            if self.stop.is_set():
                return None, None
            print(f'{time.ctime()} {worker_id} working.. {i}/3')
            await asyncio.sleep(2)

            if (i == 2 and worker_id == 4):
                print(f'{time.ctime()} EMERGENCY! Worker {worker_id} failed!')
                self.stop.set()
                return None, True


            print(f'{time.ctime()} {worker_id} completed... {i}/3')
            return time.time(), True

    async def print_task(self, worker_id, i):
        async with self.print_lock:
            print(f'{time.ctime()} {worker_id} printing.... {i}/3')
            await asyncio.sleep(10)
            print(f'{time.ctime()} {worker_id} done printing..... {i}/3')


    async def worker(self, worker_id):
        for i in range(3):
            if self.stop.is_set():
                break

            main_end, collected = await self.main_task(worker_id, i)
            if main_end is not None or (main_end is None and collected):
                task = asyncio.create_task(self.print_task(worker_id, i))
                self.print_tasks.append(task)

            if self.stop.is_set():
                break
            if main_end is not None:
                now = time.time()
                remaining_delay = max(0, (5 - (now - main_end)))
                await asyncio.sleep(remaining_delay)

    async def run(self, num_workers=5):
            self.stop.clear()
            self.print_tasks = []
            workers = [self.worker(i+1) for i in range(num_workers)]
            await asyncio.gather(*workers)
            await asyncio.gather(*self.print_tasks, return_exceptions=True)
            print(f'{time.ctime()} system stopped' if self.stop.is_set()
                  else f'{time.ctime()} All task completed.')


system = WorkerSystem()
asyncio.run(system.run())