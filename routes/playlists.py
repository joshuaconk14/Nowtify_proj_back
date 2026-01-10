"""
Playlist routes
Handles playlist-related operations
"""
from flask import Blueprint, request, session, jsonify
from services.spotify_service import SpotifyService
from utils.decorators import login_required, spotify_auth_required
from utils.validators import validate_playlist_unlink_data, ValidationError
import requests

playlists_bp = Blueprint('playlists', __name__)


def init_playlists_routes(app):
    """
    Initialize playlist routes
    
    Args:
        app: Flask application instance
    """
    @playlists_bp.route("/playlists", methods=['GET'])
    @login_required
    @spotify_auth_required
    def get_playlists():
        """Get user's Spotify playlists"""
        try:
            spotify_service = SpotifyService()
            access_token = session['access_token']
            
            # Get playlists from Spotify
            playlists = spotify_service.get_user_playlists(access_token)
            
            return jsonify(playlists), 200
            
        except requests.exceptions.HTTPError as e:
            return jsonify({
                'error': 'Failed to fetch playlists',
                'message': 'Could not retrieve playlists from Spotify'
            }), e.response.status_code if hasattr(e, 'response') else 500
        except Exception as e:
            return jsonify({
                'error': 'Playlist fetch error',
                'message': 'An error occurred while fetching playlists'
            }), 500
    
    @playlists_bp.route("/unlink-playlist", methods=['POST'])
    @login_required
    def unlink_playlist():
        """Unlink a playlist (placeholder for future implementation)"""
        try:
            # Validate input
            validated_data = validate_playlist_unlink_data(request.get_json())
            playlist_id = validated_data['playlist_id']
            
            # TODO: Implement actual unlink logic
            # This is a placeholder for future implementation
            
            return jsonify({
                'success': True,
                'message': 'Playlist successfully unlinked'
            }), 200
            
        except ValidationError as e:
            return jsonify({
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'error': 'Unlink error',
                'message': 'Failed to unlink playlist'
            }), 500
    
    app.register_blueprint(playlists_bp)

