"""
Spotify API Service
Handles all Spotify API interactions
"""
import requests
import urllib.parse
from datetime import datetime


class SpotifyService:
    """Service for interacting with Spotify API"""
    
    def __init__(self, config=None):
        """
        Initialize Spotify service
        
        Args:
            config: Flask app config object or dict with Spotify config
        """
        if config is None:
            from flask import current_app
            config = current_app.config
        
        self.client_id = config.get('SPOTIFY_CLIENT_ID')
        self.client_secret = config.get('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = config.get('SPOTIFY_REDIRECT_URI')
        self.auth_url = config.get('SPOTIFY_AUTH_URL')
        self.token_url = config.get('SPOTIFY_TOKEN_URL')
        self.api_base_url = config.get('SPOTIFY_API_BASE_URL')
    
    def get_auth_url(self, scope='user-read-private user-read-email user-library-read', show_dialog=True):
        """
        Generate Spotify authorization URL
        
        Args:
            scope: Spotify scopes (comma-separated string)
            show_dialog: Whether to show login dialog
            
        Returns:
            str: Authorization URL
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'show_dialog': show_dialog
        }
        
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_tokens(self, code):
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from Spotify callback
            
        Returns:
            dict: Token response containing access_token, refresh_token, expires_in
        """
        request_body = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.token_url, data=request_body)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token from previous authorization
            
        Returns:
            dict: New token response containing access_token, expires_in
        """
        request_body = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.token_url, data=request_body)
        response.raise_for_status()
        return response.json()
    
    def get_user_playlists(self, access_token, limit=50, offset=0):
        """
        Get user's playlists from Spotify
        
        Args:
            access_token: Spotify access token
            limit: Number of playlists to retrieve (max 50)
            offset: Offset for pagination
            
        Returns:
            dict: Playlists response from Spotify API
        """
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        url = f"{self.api_base_url}me/playlists"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def is_token_expired(self, expires_at):
        """
        Check if access token has expired
        
        Args:
            expires_at: Timestamp when token expires
            
        Returns:
            bool: True if token is expired, False otherwise
        """
        return datetime.now().timestamp() > expires_at

