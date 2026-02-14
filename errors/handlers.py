"""
Error handlers for the application
"""
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from services.auth_service import AuthService
from utils.validators import ValidationError


def register_error_handlers(app):
    """
    Register error handlers with Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        return jsonify({
            'error': 'Validation Error',
            'message': str(error)
        }), 400
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle value errors"""
        return jsonify({
            'error': 'Invalid Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """Handle database errors"""
        app.logger.error(f"Database error: {str(error)}")
        return jsonify({
            'error': 'Database Error',
            'message': 'An error occurred while processing your request'
        }), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f"Internal error: {str(error)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


