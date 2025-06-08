import asyncio
import time

from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Store(Base):
    __tablename__ = 'store'
    id = Column(Integer, autoincrement=True, primary_key=True)
    value = Column(Integer(), nullable=True)

def add_value(value: int, worker_id: int):
    session.add(Store(value = value))
    session.commit()
    print(f'{time.ctime()}--{worker_id} - {value} added...')

def init_db(db_path: str ='sqlite:///test_db.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class USERS:
    def __init__(self, user_list):
        self.user_list = user_list

    def __iter__(self):
        for i in self.user_list:
            yield i


session = init_db()

# session.add(Store(value=100))
# session.add(Store(value=100))
# session.commit()
#
# session.query(Store).all()

class NodeIterator:
    def __init__(self, db_path: str = 'nsqlite:///test_db.db', USERS = USERS(range(100))):
        self.db_path = db_path
        self.user_list = iter(USERS)
        self.print_lock = asyncio.Lock()
        self.user = None
        self.next()

    def next(self):
        self.user = next(self.user_list)



    async def work(self,worker_id: int):
        #print(f'{time.ctime()}-worker{worker_id}')
        for _ in range(5):
        #while True:
            async with self.print_lock:
                print(f'{time.ctime()}-worker {worker_id} writing to db')
                await asyncio.sleep(0.01)
                add_value(self.user, worker_id)
                try:
                    self.next()
                except StopIteration:
                    print('Copleted...')
                    break



    async def run(self):
        work_list = [i for i in range(10)]
        works = [self.work(i) for i  in work_list]
        await asyncio.gather(*works)


node = NodeIterator()
asyncio.run(node.run())
