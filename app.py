"""
Flask Application Factory
Main application entry point
"""
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

from config import ApplicationConfig
from models import db
from routes.auth import init_auth_routes
from routes.spotify import init_spotify_routes
from routes.playlists import init_playlists_routes
from errors.handlers import register_error_handlers

# Load environment variables
load_dotenv()


def create_app():
    """
    Application factory function
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(ApplicationConfig)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    
    # Configure CORS with proper origin handling
    # Support both production and development origins
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    # Strip any trailing slashes and ensure proper format
    frontend_url = frontend_url.rstrip('/')
    
    # Build allowed origins list - support both production and local development
    allowed_origins = [
        frontend_url,
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",   # Alternative localhost
    ]
    # Remove duplicates while preserving order
    allowed_origins = list(dict.fromkeys(allowed_origins))
    
    # Configure CORS with all necessary options for preflight requests
    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        max_age=3600
    )
    
    server_session = Session(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    init_auth_routes(app, bcrypt)
    init_spotify_routes(app)
    init_playlists_routes(app)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    # For development
    app.run(port=5004, debug=True)
