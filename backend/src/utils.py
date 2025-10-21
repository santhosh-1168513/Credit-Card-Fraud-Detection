"""
Utility Functions Module
Common helper functions for the application
"""

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_csv_data(df):
    """
    Validate CSV data structure
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        
    Returns:
        dict: Validation result
    """
    required_columns = ['transaction_id', 'amount', 'merchant', 'location', 'timestamp', 'card_number']
    
    if df.empty:
        return {
            'valid': False,
            'error': 'CSV file is empty'
        }
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return {
            'valid': False,
            'error': f"Missing required columns: {', '.join(missing_columns)}"
        }
    
    return {
        'valid': True,
        'error': None
    }


def generate_response(success, message=None, data=None, error=None):
    """
    Generate standardized API response
    
    Args:
        success (bool): Success status
        message (str): Response message
        data (dict): Response data
        error (str): Error message
        
    Returns:
        dict: Formatted response
    """
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return response


def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def clean_old_files(directory, max_age_hours=24):
    """
    Remove old files from directory
    
    Args:
        directory (str): Directory path
        max_age_hours (int): Maximum file age in hours
        
    Returns:
        int: Number of files deleted
    """
    try:
        deleted_count = 0
        current_time = datetime.now()
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old file: {filename}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning old files: {str(e)}")
        return 0


def create_csv_from_dict(data, filename):
    """
    Create CSV file from dictionary data
    
    Args:
        data (list): List of dictionaries
        filename (str): Output filename
        
    Returns:
        str: Path to created file
    """
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"CSV file created: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to create CSV: {str(e)}")
        raise


def log_request(request):
    """
    Log incoming HTTP request details
    
    Args:
        request: Flask request object
    """
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")


def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal attacks
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove directory components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    return filename