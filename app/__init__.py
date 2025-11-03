"""
Flask application factory for Q_FEA Web Application
"""

import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from app.config import config


def create_app(config_name='default'):
    """
    Create and configure Flask application

    Args:
        config_name: Configuration name (development, production, testing, default)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Q_FEA application in {config_name} mode")

    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register main routes
    @app.route('/')
    def index():
        """Render main application page"""
        return render_template('index.html')

    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Q_FEA Web Application',
            'version': '1.0.0'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error': str(error)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(error)
        }), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file too large errors"""
        return jsonify({
            'success': False,
            'message': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.0f}MB',
            'error': str(error)
        }), 413

    return app
