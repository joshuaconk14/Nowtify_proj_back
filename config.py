# separate config file so can determine environment settings, security, app behavior, etc.

from dotenv import load_dotenv
import os
try:
    import redis
except ImportError:
    redis = None  # Redis is optional if using filesystem sessions

load_dotenv()

# Determine environment (development or production)
# Railway sets RAILWAY_ENVIRONMENT, Heroku uses FLASK_ENV
ENV = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("FLASK_ENV", "development")


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
    SESSION_COOKIE_PATH = '/'  # Cookie available for all paths
    
    # Session storage: Use Redis if available, otherwise fall back to filesystem
    # Railway uses REDIS_URL, Heroku uses REDISCLOUD_URL
    redis_url = os.environ.get("REDIS_URL") or os.environ.get("REDISCLOUD_URL")
    
    if redis_url and redis:
        # Use Redis if URL is provided (better for production, especially with multiple instances)
        SESSION_TYPE = 'redis'
        SESSION_REDIS = redis.from_url(redis_url)
        # Cookie settings for production HTTPS with cross-origin
        SESSION_COOKIE_SECURE = True  # True for production HTTPS
        SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-site cookies with HTTPS
        SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
        SESSION_COOKIE_DOMAIN = None  # None allows cross-origin cookies to work
    else:
        # Fall back to filesystem sessions (works fine for single-instance deployments)
        SESSION_TYPE = 'filesystem'
        SESSION_FILE_DIR = './flask_session'  # Directory to store session files
        # Cookie settings based on environment
        if ENV == "development":
            SESSION_COOKIE_SECURE = False  # False for local HTTP development
            SESSION_COOKIE_SAMESITE = 'Lax'  # Lax is fine for local development
            SESSION_COOKIE_HTTPONLY = True
            SESSION_COOKIE_DOMAIN = None
        else:
            # Production cookie settings for cross-origin HTTPS
            SESSION_COOKIE_SECURE = True  # True for production HTTPS
            SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-site cookies with HTTPS
            SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
            SESSION_COOKIE_DOMAIN = None  # None allows cross-origin cookies to work
    
    # --Frontend-- (for OAuth redirects back to app)
    FRONTEND_URL = (os.environ.get("FRONTEND_URL") or "http://localhost:3000").rstrip("/")

    # --Spotify API-- configurations
    SPOTIFY_CLIENT_ID = os.environ.get("CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    # Redirect URI where Spotify sends the user (must match Spotify dashboard). Use frontend
    # callback so the request lands on same origin as the session cookie.
    SPOTIFY_REDIRECT_URI = os.environ.get("REDIRECT_URI") or (FRONTEND_URL + "/spotify-callback")
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"
