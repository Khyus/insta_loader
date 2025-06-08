from db import User, init_db

class DB_iterable:
    def __init__(self, db_path):
        self.db_path = db_path
        self.user_list = self.generate_user_list()


    def generate_user_list(self):
        session = init_db(self.db_path)
        return session.query(User).all()

    def __iter__(self):
        for user in self.user_list:
            yield user
        #return DB_iterator(self.user_list)
#
#
# class DB_iterator:
#     def __init__(self, user_list):
#         self.user_list = user_list
#         self.index = 0
#
#     def __next__(self):
#         try:
#             user = self.user_list[self.index]
#         except IndexError:
#             raise StopIteration()
#         self.index += 1
#         return user
#
#     def __iter__(self):
#         return self



db_iteratable = DB_iterable('sqlite:///moses.db')
db_iterator = iter(db_iteratable)
next(db_iterator)
