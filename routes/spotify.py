"""
Spotify OAuth routes
Handles Spotify authentication and token management
"""
from flask import Blueprint, request, session, jsonify, redirect
from services.spotify_service import SpotifyService
from utils.decorators import login_required
from datetime import datetime
import requests

spotify_bp = Blueprint('spotify', __name__)


def init_spotify_routes(app):
    """
    Initialize Spotify routes
    
    Args:
        app: Flask application instance
    """
    # SpotifyService will use current_app.config when called from route handlers
    
    @spotify_bp.route("/spotify-login", methods=['GET'])
    @login_required
    def spotify_login():
        """Initiate Spotify OAuth flow"""
        try:
            spotify_service = SpotifyService()
            scope = 'user-read-private user-read-email user-library-read'
            auth_url = spotify_service.get_auth_url(scope=scope, show_dialog=True)
            return jsonify({'auth_url': auth_url}), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to generate Spotify auth URL',
                'message': str(e)
            }), 500
    
    @spotify_bp.route("/callback", methods=['GET'])
    @login_required
    def callback():
        """Handle Spotify OAuth callback"""
        try:
            # Check for errors
            if 'error' in request.args:
                return jsonify({
                    "error": "Failed to login",
                    "message": request.args['error']
                }), 400
            
            # Exchange code for tokens
            if 'code' in request.args:
                spotify_service = SpotifyService()
                code = request.args['code']
                token_response = spotify_service.exchange_code_for_tokens(code)
                
                # Store tokens in session
                session['access_token'] = token_response['access_token']
                session['refresh_token'] = token_response.get('refresh_token')
                session['expires_at'] = datetime.now().timestamp() + token_response['expires_in']
                
                return jsonify({'success': True}), 200
            else:
                return jsonify({
                    'error': 'Missing authorization code',
                    'message': 'No authorization code received from Spotify'
                }), 400
                
        except requests.exceptions.HTTPError as e:
            return jsonify({
                'error': 'Spotify API error',
                'message': 'Failed to exchange authorization code for tokens'
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Callback error',
                'message': 'An error occurred during Spotify callback'
            }), 500
    
    @spotify_bp.route("/refresh-token", methods=['GET', 'POST'])
    @login_required
    def refresh_token():
        """Refresh Spotify access token"""
        try:
            if 'refresh_token' not in session:
                return jsonify({
                    'error': 'No refresh token',
                    'message': 'Please connect your Spotify account first'
                }), 401
            
            # Check if token is expired
            expires_at = session.get('expires_at', 0)
            if datetime.now().timestamp() > expires_at:
                spotify_service = SpotifyService()
                refresh_token_value = session['refresh_token']
                token_response = spotify_service.refresh_access_token(refresh_token_value)
                
                # Update session with new tokens
                session['access_token'] = token_response['access_token']
                if 'refresh_token' in token_response:
                    session['refresh_token'] = token_response['refresh_token']
                session['expires_at'] = datetime.now().timestamp() + token_response.get('expires_in', 3600)
                
                return jsonify({'success': True, 'message': 'Token refreshed'}), 200
            else:
                return jsonify({'message': 'Token is still valid'}), 200
                
        except requests.exceptions.HTTPError as e:
            return jsonify({
                'error': 'Token refresh failed',
                'message': 'Failed to refresh Spotify token. Please reconnect your account.'
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Refresh error',
                'message': 'An error occurred while refreshing token'
            }), 500
    
    app.register_blueprint(spotify_bp)

