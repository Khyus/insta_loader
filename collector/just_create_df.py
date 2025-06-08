import pandas as pd
from db import User, init_db
from sqlalchemy import text


name = 'visitalburywodonga'
session = init_db(name)
query = text('''
SELECT user_id, username, bio, is_private, is_verified, is_professional_account, is_business_account, business_address, category_name, category_enum
FROM users;
''')

#data = session.query(User.user_id, User.username, User.bio, User.is_private).all()
data = session.execute(query).fetchall()

df = pd.DataFrame(data=data, columns=['user_id','username','bio','is_private','is_verified','is_professional_account', 'is_business_account', 'business_address','category_name','category_enum'])
df['url'] = 'https://www.instagram.com/' + df['username'] + '/'

df.to_csv(name+'.csv')

