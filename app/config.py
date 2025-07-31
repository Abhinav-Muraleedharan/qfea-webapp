"""
Configuration settings for Q_FEA Web Application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = Path(__file__).parent.parent

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    WORKERS = int(os.environ.get('WORKERS') or 4)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = basedir / 'app' / 'static' / 'uploads'
    ALLOWED_EXTENSIONS = {'vtk', 'mesh', 'msh', 'obj', 'stl', 'ply'}
    
    # Redis settings (for task queue)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Database settings (optional)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///qfea.db'
    
    # Quantum simulation settings
    MAX_QUBITS = int(os.environ.get('MAX_QUBITS') or 20)
    MAX_PAULI_TERMS = int(os.environ.get('MAX_PAULI_TERMS') or 1000)
    DEFAULT_TROTTER_STEPS = int(os.environ.get('DEFAULT_TROTTER_STEPS') or 10)
    
    # Computational settings
    USE_GPU = os.environ.get('USE_GPU', 'False').lower() == 'true'
    MAX_PARALLEL_JOBS = int(os.environ.get('MAX_PARALLEL_JOBS') or 4)
    COMPUTATION_TIMEOUT = int(os.environ.get('COMPUTATION_TIMEOUT') or 3600)  # 1 hour
    
    # Material presets
    MATERIAL_PRESETS = {
        'steel': {
            'young_modulus': 200e9,  # Pa
            'poisson_ratio': 0.3,
            'density': 7850,  # kg/m³
            'description': 'Structural steel'
        },
        'aluminum': {
            'young_modulus': 70e9,
            'poisson_ratio': 0.33,
            'density': 2700,
            'description': 'Aluminum alloy'
        },
        'concrete': {
            'young_modulus': 30e9,
            'poisson_ratio': 0.2,
            'density': 2400,
            'description': 'Normal weight concrete'
        },
        'titanium': {
            'young_modulus': 110e9,
            'poisson_ratio': 0.34,
            'density': 4500,
            'description': 'Titanium alloy'
        },
        'copper': {
            'young_modulus': 110e9,
            'poisson_ratio': 0.35,
            'density': 8960,
            'description': 'Pure copper'
        }
    }
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create upload directory if it doesn't exist
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Override with more secure settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    
    # Use stronger session protection
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    FLASK_ENV = 'testing'
    UPLOAD_FOLDER = basedir / 'tests' / 'temp'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}