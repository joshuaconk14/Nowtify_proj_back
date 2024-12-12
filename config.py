# separate config file so can determine environment settings, security, app behavior, etc.

from dotenv import load_dotenv
import os
import redis
from urllib.parse import quote # for my password, to pass through its @ and ! symbols

load_dotenv()

password = quote(os.environ.get("SQL_PASSWORD"))
username = os.environ.get("SQL_USERNAME")
address = os.environ.get("SQL_ADDRESS")
db_name = os.environ.get("SQL_DB_NAME")



class ApplicationConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") # using secret key from .env

    # --database-- configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False # stops running useless messages
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f'mysql+mysqlconnector://{username}:{password}@{address}/{db_name}')

    # --session-- configurations
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False # dont want session to be permanent, will end when user logs out
    SESSION_USE_SIGNER = True # uses secret key signer to allow access into app
    SESSION_REDIS = redis.from_url(os.environ.get("REDISCLOUD_URL")) # redis URL, pointing to redis client

    SESSION_COOKIE_SAMESITE = 'None' # now set to cross-site cookies, so can enable user sessions on diff domains, required for HTTPS secure session cookie to work (set to True)
    # made /@me route work (need to run HTTPS for this to work)
    SESSION_COOKIE_SECURE = True # set to false for HTTP only, but turned to TRUE for cross-site cookies so only send cookies over HTTPS (cross-site cookies require this)
    PERMANENT_SESSION_LIFETIME = 3600 # session will last for 1 hour