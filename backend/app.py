"""
Main Flask application for Personal Finance App
Sets up the Flask app, database, and registers API routes
"""

from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from routes import api
import os

def create_app():
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Use absolute path for database to avoid conflicts
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'finance_app.db')
    # db_path = db_path.replace('\\', '/')  # Normalize for Windows to ensure persistence
    db_path = db_path.replace('\\', '/')  # Normalize for Windows to ensure persistence
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Personal Finance App API',
            'version': '1.0.0',
            'endpoints': {
                'categories': '/api/categories',
                'transactions': '/api/transactions',
                'investments': '/api/investments',
                'dashboard': '/api/dashboard',
                'analytics': {
                    'spending_trends': '/api/analytics/spending-trends',
                    'investment_performance': '/api/analytics/investment-performance'
                }
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db.engine else 'disconnected'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created/verified!")
    
    # Run the application
    print("Starting Personal Finance App...")
    print("API available at: http://localhost:5000")
    print("Health check at: http://localhost:5000/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
