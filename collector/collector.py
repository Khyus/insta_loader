import instaloader
from db import add_user, add_followings, User, init_db



loader = instaloader.Instaloader()
session = None
# loader.login('she_smiles33','fadh2005')

def login(username: str, passwd: str):
    loader.login(username, passwd)
    return loader

def initilize_db(db_path: str = 'sqlite:///:memory:'):
    session = init_db(db_path)
    return session

def collect_followers(session, account_username):
    profile = instaloader.Profile.from_username(loader.context, account_username)
    count = profile.followers

    for i,follower in enumerate(profile.get_followers()):
        print(f'{i}/{count}', end='\r')
        add_user(session = session, username=follower.username,bio=follower.biography,
                 original_followers=True, is_private=follower.is_private, is_verified=follower.is_verified)




def oollect_followings(session):

    users = session.query(User).all()
    followers_usernames = [u for u in users if u.original_followers == True and u.state == 'empty']
    count = 0
    for follower in followers_usernames:
        count += 1
        follower_profile = instaloader.Profile.from_username(loader.context, follower.username)
        num_follower_followee = follower_profile.followees
        follower.state = 'in-progress'
        session.commit()

        for i, following in enumerate(follower_profile.get_followees()):
            print(f'{i}/{num_follower_followee}------> {follower.username}', end='\r')
            add_followings(session, follower.username, following.username,following.biography, following.is_private, following.is_verified)

        if len(follower.following) == num_follower_followee:
            follower.state = 'completed'
        if len(follower.following) >= int(num_follower_followee*0.9):     # 90% collected.
            follower.state = 'almost'

        if count > 40:
            break


