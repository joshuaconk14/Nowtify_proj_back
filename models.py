# this is where we create the database models for user's usernames and passwords

from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4



db = SQLAlchemy() # database instance to initialize it for app

# function that creates unique identifier for user ID
def get_uuid():
    return uuid4().hex

# class for user database model, creating table for database
    # Usermixinhandles user auth, session tracking, etc
    # nullable = false means cannot leave blank
class User(db.Model):
    id = db.Column(db.String(36), primary_key = True, unique = True, default = get_uuid)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(128), nullable = False)






    # def __repr__(self):
    #     return f'<User {self.username}>' # ??