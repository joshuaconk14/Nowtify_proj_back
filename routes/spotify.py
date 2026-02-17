"""
Spotify OAuth routes
Handles Spotify authentication and token management
"""
from flask import Blueprint, request, session, jsonify, redirect, current_app
from urllib.parse import urlencode
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
            scope = (
                'user-read-private user-read-email user-library-read '
                'playlist-read-private playlist-read-collaborative'
            )
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
        """Legacy: backend callback (only works when request has session cookie, e.g. same origin as login)."""
        frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
        dashboard_url = f"{frontend_url}/dashboard"
        def redirect_to_dashboard(success=None, error=None):
            params = {}
            if success:
                params["spotify"] = "connected"
            if error:
                params["error"] = error
            url = f"{dashboard_url}?{urlencode(params)}" if params else dashboard_url
            return redirect(url)
        try:
            if 'error' in request.args:
                return redirect_to_dashboard(error=request.args.get('error', 'spotify_denied'))
            if 'code' not in request.args:
                return redirect_to_dashboard(error="no_code")
            code = request.args['code']
            spotify_service = SpotifyService()
            token_response = spotify_service.exchange_code_for_tokens(code)
            session['access_token'] = token_response['access_token']
            session['refresh_token'] = token_response.get('refresh_token')
            session['expires_at'] = datetime.now().timestamp() + token_response['expires_in']
            return redirect_to_dashboard(success=True)
        except requests.exceptions.HTTPError:
            return redirect_to_dashboard(error="token_exchange_failed")
        except Exception:
            return redirect_to_dashboard(error="callback_error")

    @spotify_bp.route("/spotify-exchange", methods=['POST'])
    @login_required
    def spotify_exchange():
        """
        Exchange Spotify auth code for tokens. Called by the frontend after user is
        redirected to the frontend with ?code=... so the request carries the session cookie.
        """
        frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
        dashboard_url = f"{frontend_url}/dashboard"
        data = request.get_json() or {}
        code = data.get("code")
        if not code:
            return jsonify({"error": "Missing code", "message": "No authorization code"}), 400
        try:
            spotify_service = SpotifyService()
            token_response = spotify_service.exchange_code_for_tokens(code)
            session['access_token'] = token_response['access_token']
            session['refresh_token'] = token_response.get('refresh_token')
            session['expires_at'] = datetime.now().timestamp() + token_response['expires_in']
            return jsonify({"success": True, "redirect": dashboard_url}), 200
        except requests.exceptions.HTTPError:
            return jsonify({"error": "Token exchange failed"}), 400
        except Exception:
            return jsonify({"error": "Callback error"}), 500
    
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

