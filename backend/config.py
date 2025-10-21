"""
Configuration Module
Application configuration settings
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # File Upload Settings
    UPLOAD_FOLDER = 'uploads'
    MODEL_FOLDER = 'models'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Model Settings
    MODEL_TYPE = 'random_forest'  # Options: 'random_forest', 'logistic_regression'
    TEST_SIZE = 0.2  # Train-test split ratio
    
    # CORS Settings
    CORS_ORIGINS = '*'
    
    # Logging Settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'fraudguard.log'
    
    # Session Settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # File Cleanup Settings
    AUTO_CLEANUP = True
    MAX_FILE_AGE_HOURS = 24  # Remove files older than 24 hours


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Stricter CORS in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://yourdomain.com')
    
    # Production logging
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use separate folders for testing
    UPLOAD_FOLDER = 'test_uploads'
    MODEL_FOLDER = 'test_models'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}