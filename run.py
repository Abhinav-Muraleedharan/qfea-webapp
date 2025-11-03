#!/usr/bin/env python3
"""
Application entry point for Q_FEA Web Application
"""

import os
from app import create_app

# Get configuration from environment variable, default to development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Get host and port from config
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)

    print(f"Starting Q_FEA Web Application")
    print(f"Environment: {config_name}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"API endpoint: http://{host}:{port}/api")
    print(f"Health check: http://{host}:{port}/health")

    app.run(host=host, port=port, debug=debug)
