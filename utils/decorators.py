"""
Decorators for route protection and authentication
"""
from functools import wraps
from flask import session, jsonify, redirect
from datetime import datetime


def login_required(f):
    """
    Decorator to require user login for a route
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Please log in to access this resource'}), 401
        return f(*args, **kwargs)
    return decorated_function


def spotify_auth_required(f):
    """
    Decorator to require Spotify authentication for a route
    Checks if access token exists and is not expired
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return jsonify({
                'error': 'Spotify not connected',
                'message': 'Please connect your Spotify account'
            }), 401
        
        # Check if token is expired
        expires_at = session.get('expires_at')
        if expires_at and datetime.now().timestamp() > expires_at:
            return jsonify({
                'error': 'Token expired',
                'message': 'Spotify token has expired. Please reconnect.'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


