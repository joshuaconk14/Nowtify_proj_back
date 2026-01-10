"""
Authentication routes
Handles user registration, login, logout, and current user info
"""
from flask import Blueprint, request, session, jsonify
from services.auth_service import AuthService
from utils.decorators import login_required
from utils.validators import validate_register_data, validate_login_data, ValidationError
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)


def init_auth_routes(app, bcrypt_instance):
    """
    Initialize authentication routes with dependencies
    
    Args:
        app: Flask application instance
        bcrypt_instance: Bcrypt instance for password hashing
    """
    @auth_bp.route("/@me", methods=['GET'])
    @login_required
    def get_current_user():
        """Get current logged-in user information"""
        auth_service = AuthService(bcrypt_instance)
        user_id = session.get('user_id')
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'logged_in': False}), 401
        
        return jsonify({
            'logged_in': True,
            'id': user.id,
            'username': user.username
        }), 200
    
    @auth_bp.route("/register", methods=['POST'])
    def register():
        """Register a new user"""
        try:
            auth_service = AuthService(bcrypt_instance)
            # Validate input
            validated_data = validate_register_data(request.json)
            
            # Register user
            new_user = auth_service.register_user(
                validated_data['username'],
                validated_data['password']
            )
            
            # Set session
            session['user_id'] = new_user.id
            
            return jsonify({
                'id': new_user.id,
                'username': new_user.username
            }), 201
            
        except ValidationError as e:
            return jsonify({'message': str(e)}), 400
        except ValueError as e:
            return jsonify({'message': str(e)}), 400
        except Exception as e:
            # Log the actual error for debugging
            import traceback
            error_msg = str(e)
            print(f"Registration error: {error_msg}")
            print(traceback.format_exc())
            return jsonify({'message': f'An error occurred during registration: {error_msg}'}), 500
    
    @auth_bp.route("/user-login", methods=['POST'])
    def login():
        """Login user"""
        try:
            auth_service = AuthService(bcrypt_instance)
            # Validate input
            validated_data = validate_login_data(request.json)
            
            # Authenticate user
            user = auth_service.authenticate_user(
                validated_data['username'],
                validated_data['password']
            )
            
            if user:
                session['user_id'] = user.id
                return jsonify({
                    'logged_in': True,
                    'id': user.id,
                    'username': user.username
                }), 200
            else:
                return jsonify({'message': 'Invalid username or password.'}), 401
                
        except ValidationError as e:
            return jsonify({'message': str(e)}), 400
        except Exception as e:
            return jsonify({'message': 'An error occurred during login'}), 500
    
    @auth_bp.route('/logout', methods=['POST'])
    @login_required
    def logout():
        """Logout user"""
        session.pop('user_id', None)
        session.pop('access_token', None)
        session.pop('refresh_token', None)
        session.pop('expires_at', None)
        return jsonify({'message': 'Logged out'}), 200
    
    app.register_blueprint(auth_bp)

