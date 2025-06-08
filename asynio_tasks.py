import asyncio
import time

async def say_hello(worker_id, lock):
    async with lock:
        await asyncio.sleep(3)
        return f'Hello, World- {worker_id}'

async def print(worke_id):
    await asyncio.sleep(10)
    print(f'{time.ctime()}Done')

async def main(worker_id, lock):
    while True:
        task = asyncio.create_task(say_hello(worker_id,lock))
        result = await task
        print(f'{time.ctime()} Task {result}')

async def run():
    lock = asyncio.Lock()
    workers = [main(i, lock) for i in range(3)]
    await asyncio.gather(*workers)

asyncio.run(run())