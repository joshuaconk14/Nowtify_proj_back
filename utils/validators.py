"""
Input validation utilities
"""
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_register_data(data):
    """
    Validate user registration data
    
    Args:
        data: Dictionary containing username and password
        
    Raises:
        ValidationError: If validation fails
    """
    if not data:
        raise ValidationError("Request body is required")
    
    if 'username' not in data or not data['username']:
        raise ValidationError("Username is required")
    
    if 'password' not in data or not data['password']:
        raise ValidationError("Password is required")
    
    username = data['username'].strip()
    password = data['password']
    
    # Username validation
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")
    
    if len(username) > 20:
        raise ValidationError("Username must be no more than 20 characters long")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    
    # Password validation
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long")
    
    return {
        'username': username,
        'password': password
    }


def validate_login_data(data):
    """
    Validate user login data
    
    Args:
        data: Dictionary containing username and password
        
    Raises:
        ValidationError: If validation fails
    """
    if not data:
        raise ValidationError("Request body is required")
    
    if 'username' not in data or not data['username']:
        raise ValidationError("Username is required")
    
    if 'password' not in data or not data['password']:
        raise ValidationError("Password is required")
    
    return {
        'username': data['username'].strip(),
        'password': data['password']
    }


def validate_playlist_unlink_data(data):
    """
    Validate playlist unlink data
    
    Args:
        data: Dictionary containing playlist ID
        
    Raises:
        ValidationError: If validation fails
    """
    if not data:
        raise ValidationError("Request body is required")
    
    playlist_id = data.get('p') or data.get('playlist_id')
    
    if not playlist_id:
        raise ValidationError("Playlist ID is required")
    
    return {'playlist_id': playlist_id}


