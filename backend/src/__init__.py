"""
FraudGuard Source Package
Contains core fraud detection modules
"""

__version__ = '1.0.0'
__author__ = 'FraudGuard Team'

# Import modules directly without relative imports to avoid issues
import sys
import os
sys.path.append(os.path.dirname(__file__))

from data_processor import DataProcessor
from model_manager import ModelManager
from fraud_detector import FraudDetector
from utils import allowed_file, validate_csv_data, generate_response

__all__ = [
    'DataProcessor',
    'ModelManager',
    'FraudDetector',
    'allowed_file',
    'validate_csv_data',
    'generate_response'
]
