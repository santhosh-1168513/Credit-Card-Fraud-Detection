
"""
FraudGuard - Credit Card Fraud Detection System
Flask Backend Server
Author: Production Team
Version: 1.0.0
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Import custom modules
from src.data_processor import DataProcessor
from src.model_manager import ModelManager
from src.fraud_detector import FraudDetector
from src.utils import allowed_file, validate_csv_data, generate_response

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraudguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
data_processor = DataProcessor()
model_manager = ModelManager(app.config['MODEL_FOLDER'])
fraud_detector = FraudDetector(model_manager)


# =====================================================
# API ROUTES
# =====================================================

@app.route('/')
def index():
    """
    Root endpoint - API information
    """
    return jsonify({
        'name': 'FraudGuard API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'upload': '/api/upload',
            'predict': '/api/predict',
            'train': '/api/train',
            'model_info': '/api/model/info',
            'statistics': '/api/statistics'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns: JSON with system status
    """
    try:
        model_loaded = model_manager.is_model_loaded()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model_loaded': model_loaded,
            'uptime': 'operational'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload CSV file endpoint
    Accepts: CSV file via form-data
    Returns: JSON with upload status and file info
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file has a name
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transactions_{timestamp}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        logger.info(f"File uploaded successfully: {filename}")
        
        # Get file info
        file_size = os.path.getsize(filepath)
        
        # Read and validate CSV
        df = data_processor.read_csv(filepath)
        row_count = len(df)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_info': {
                'filename': filename,
                'filepath': filepath,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'row_count': row_count,
                'upload_time': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Fraud prediction endpoint
    Accepts: JSON with filepath or CSV file
    Returns: JSON with fraud detection results
    """
    try:
        # Check if model is loaded
        if not model_manager.is_model_loaded():
            # Try to load existing model
            if not model_manager.load_model():
                return jsonify({
                    'success': False,
                    'error': 'No trained model available. Please train a model first.'
                }), 400
        
        # Get filepath from request
        filepath = None
        
        if 'file' in request.files:
            # File upload
            file = request.files['file']
            if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"predict_{timestamp}.csv"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        elif request.json and 'filepath' in request.json:
            # Filepath provided
            filepath = request.json['filepath']
        else:
            return jsonify({
                'success': False,
                'error': 'No file or filepath provided'
            }), 400
        
        # Validate filepath
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Read and process data
        df = data_processor.read_csv(filepath)
        logger.info(f"Processing {len(df)} transactions for prediction")
        
        # Validate CSV structure
        validation_result = validate_csv_data(df)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': f"Invalid CSV structure: {validation_result['error']}"
            }), 400
        
        # Perform fraud detection
        results = fraud_detector.predict(df)
        
        logger.info(f"Prediction completed: {results['summary']['fraud_count']} frauds detected")
        
        return jsonify({
            'success': True,
            'message': 'Fraud detection completed successfully',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500


@app.route('/api/train', methods=['POST'])
def train_model():
    """
    Model training endpoint
    Accepts: CSV file with labeled data (requires 'is_fraud' column)
    Returns: JSON with training results and model metrics
    """
    try:
        # Get file from request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No training file provided'
            }), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400
        
        # Save training file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"training_data_{timestamp}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read data
        df = data_processor.read_csv(filepath)
        logger.info(f"Training model with {len(df)} samples")
        
        # Check for label column
        if 'is_fraud' not in df.columns:
            return jsonify({
                'success': False,
                'error': 'Training data must contain "is_fraud" column with labels (0 or 1)'
            }), 400
        
        # Train model
        training_results = fraud_detector.train(df)
        
        logger.info(f"Model training completed with accuracy: {training_results['metrics']['accuracy']:.4f}")
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'results': training_results
        }), 200
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Training failed: {str(e)}'
        }), 500


@app.route('/api/model/info', methods=['GET'])
def model_info():
    """
    Get model information
    Returns: JSON with model details and statistics
    """
    try:
        if not model_manager.is_model_loaded():
            return jsonify({
                'success': False,
                'error': 'No model loaded'
            }), 404
        
        info = model_manager.get_model_info()
        
        return jsonify({
            'success': True,
            'model_info': info
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Get system statistics
    Returns: JSON with usage statistics
    """
    try:
        stats = {
            'total_predictions': fraud_detector.get_prediction_count(),
            'model_loaded': model_manager.is_model_loaded(),
            'upload_folder_size': sum(
                os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
                for f in os.listdir(app.config['UPLOAD_FOLDER'])
                if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))
            ),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    logger.info("Starting FraudGuard Backend Server...")
    
    # Try to load existing model on startup
    if model_manager.load_model():
        logger.info("Existing model loaded successfully")
    else:
        logger.info("No existing model found. Train a model using /api/train endpoint")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )