# separate config file so can determine environment settings, security, app behavior, etc.

from dotenv import load_dotenv
import os
import redis

load_dotenv()

# Determine environment (development or production)
ENV = os.environ.get("FLASK_ENV", "development")


class ApplicationConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")  # using secret key from .env

    # --database-- configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # stops running useless messages
    
    # Database configuration: SQLite for dev, PostgreSQL for production
    if ENV == "development":
        # SQLite for local development (no setup needed)
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", 
            "sqlite:///app.db"  # Default to SQLite if DATABASE_URL not set
        )
    else:
        # PostgreSQL for production (must be set via DATABASE_URL)
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
        if not SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL must be set in production environment")

    # --session-- configurations
    SESSION_PERMANENT = False  # dont want session to be permanent, will end when user logs out
    SESSION_USE_SIGNER = True  # uses secret key signer to allow access into app
    PERMANENT_SESSION_LIFETIME = 3600  # session will last for 1 hour
    
    # Use filesystem sessions for local dev, Redis for production
    if ENV == "development":
        SESSION_TYPE = 'filesystem'  # No Redis needed for local development
        SESSION_FILE_DIR = './flask_session'  # Directory to store session files
        SESSION_COOKIE_SECURE = False  # False for local HTTP development
        SESSION_COOKIE_SAMESITE = 'Lax'  # Lax is fine for local development
    else:
        SESSION_TYPE = 'redis'  # Redis for production
        redis_url = os.environ.get("REDISCLOUD_URL")
        if not redis_url:
            raise ValueError("REDISCLOUD_URL must be set in production environment")
        SESSION_REDIS = redis.from_url(redis_url)  # redis URL, pointing to redis client
        SESSION_COOKIE_SECURE = True  # True for production HTTPS
        SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-site cookies with HTTPS
    
    # --Spotify API-- configurations
    SPOTIFY_CLIENT_ID = os.environ.get("CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.environ.get("REDIRECT_URI")
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"