from db import User, init_db

class DB_iterable:
    def __init__(self, session):
        self.session = session
        self.user_list = self.generate_user_list()


    def generate_user_list(self):
        return self.session.query(User).all()

    def __iter__(self):
        # for user in self.user_list:
        #     yield user
        return DB_iterator(self.user_list)
#
#
class DB_iterator:
    def __init__(self, user_list):
        self.user_list = user_list
        self.index = 0

    def __next__(self):
        try:
            user = self.user_list[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return user

    def __iter__(self):
        return self

    def next_user(self):
        return next(self)





