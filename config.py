# separate config file so can determine environment settings, security, app behavior, etc.

from dotenv import load_dotenv
import os
import redis
from urllib.parse import quote # for my password since theres an @ in it

load_dotenv()

password = quote("SQL_PASSWORD")

class ApplicationConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") # using secret key from .env

    # --database-- configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False # stops running useless messages
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f'mysql+mysqlconnector://joshuaconk7:{password}@nowtify-db-test.cfaiue6qsrin.us-west-1.rds.amazonaws.com/nowtify-DB-test') # getting heroku database url from env + specifying which MySQL db to connect to

    # --session-- configurations
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False # dont want session to be permanent, will end when user logs out
    SESSION_USE_SIGNER = True # uses secret key signer to allow access into app
    SESSION_REDIS = redis.from_url('redis://127.0.0.1:6379') # redis URL, pointing to redis client

    SESSION_COOKIE_SAMESITE = 'None' # now set to cross-site cookies, so can enable user sessions on diff domains, required for HTTPS secure session cookie to work (set to True)
    # made /@me route work (need to run HTTPS for this to work)
    SESSION_COOKIE_SECURE = True # set to false for HTTP only, but turned to TRUE for cross-site cookies so only send cookies over HTTPS (cross-site cookies require this)
    PERMANENT_SESSION_LIFETIME = 3600 # session will last for 1 hour