"""
Authentication Service
Handles user authentication and registration logic
"""
from flask_bcrypt import Bcrypt
from models import db, User


class AuthService:
    """Service for user authentication and registration"""
    
    def __init__(self, bcrypt_instance):
        self.bcrypt = bcrypt_instance
    
    def register_user(self, username, password):
        """
        Register a new user
        
        Args:
            username: Username for new user
            password: Plain text password
            
        Returns:
            User: Newly created user object
            
        Raises:
            ValueError: If username already exists
        """
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValueError("Username already exists")
        
        # Hash password and create user
        hashed_password = self.bcrypt.generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User: Authenticated user object if credentials are valid, None otherwise
        """
        user = User.query.filter_by(username=username).first()
        
        if user and self.bcrypt.check_password_hash(user.password, password):
            return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User: User object if found, None otherwise
        """
        return User.query.filter_by(id=user_id).first()


