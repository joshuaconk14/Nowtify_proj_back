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
    CORS(app, supports_credentials=True, origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")])
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

