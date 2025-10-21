"""
Data Processing Module
Handles CSV reading, data preprocessing, and feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Handles all data processing operations for fraud detection
    """
    
    def __init__(self):
        """Initialize DataProcessor"""
        self.required_columns = [
            'transaction_id', 'amount', 'merchant', 
            'location', 'timestamp', 'card_number'
        ]
        logger.info("DataProcessor initialized")
    
    def read_csv(self, filepath):
        """
        Read CSV file and return pandas DataFrame
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            Exception: If file cannot be read
        """
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Successfully read CSV file: {filepath} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Failed to read CSV file {filepath}: {str(e)}")
            raise Exception(f"Failed to read CSV file: {str(e)}")
    
    def validate_data(self, df):
        """
        Validate DataFrame structure and content
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("CSV file is empty")
            return {'valid': False, 'errors': errors}
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for null values in critical columns
        critical_columns = ['transaction_id', 'amount', 'timestamp']
        for col in critical_columns:
            if col in df.columns and df[col].isnull().any():
                errors.append(f"Column '{col}' contains null values")
        
        # Validate data types
        if 'amount' in df.columns:
            try:
                pd.to_numeric(df['amount'], errors='raise')
            except:
                errors.append("Column 'amount' must contain numeric values")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation failed: {errors}")
        
        return {'valid': is_valid, 'errors': errors}
    
    def preprocess_data(self, df):
        """
        Preprocess data for model input
        
        Args:
            df (pd.DataFrame): Raw input DataFrame
            
        Returns:
            pd.DataFrame: Preprocessed DataFrame with engineered features
        """
        try:
            # Create a copy to avoid modifying original data
            df_processed = df.copy()
            
            # Convert amount to float
            if 'amount' in df_processed.columns:
                df_processed['amount'] = pd.to_numeric(df_processed['amount'], errors='coerce')
            
            # Parse timestamp and extract features
            if 'timestamp' in df_processed.columns:
                df_processed['timestamp'] = pd.to_datetime(df_processed['timestamp'], errors='coerce')
                df_processed['hour'] = df_processed['timestamp'].dt.hour
                df_processed['day_of_week'] = df_processed['timestamp'].dt.dayofweek
                df_processed['day_of_month'] = df_processed['timestamp'].dt.day
                df_processed['month'] = df_processed['timestamp'].dt.month
            
            # Engineer amount-based features
            if 'amount' in df_processed.columns:
                df_processed['amount_log'] = np.log1p(df_processed['amount'])
                df_processed['amount_rounded'] = df_processed['amount'].round(-1)  # Round to nearest 10
                
                # Flag unusual amounts
                df_processed['is_large_amount'] = (df_processed['amount'] > 5000).astype(int)
                df_processed['is_small_amount'] = (df_processed['amount'] < 10).astype(int)
            
            # Encode categorical variables
            if 'merchant' in df_processed.columns:
                df_processed['merchant_encoded'] = pd.Categorical(df_processed['merchant']).codes
            
            if 'location' in df_processed.columns:
                df_processed['location_encoded'] = pd.Categorical(df_processed['location']).codes
                
                # High-risk location detection (simplified)
                high_risk_locations = ['Nigeria', 'Russia', 'Ukraine', 'Unknown']
                df_processed['is_high_risk_location'] = df_processed['location'].apply(
                    lambda x: 1 if any(loc in str(x) for loc in high_risk_locations) else 0
                )
            
            # Velocity features (transactions per hour - simplified demo)
            if 'card_number' in df_processed.columns and 'timestamp' in df_processed.columns:
                # Count transactions per card
                df_processed['transaction_count'] = df_processed.groupby('card_number').cumcount() + 1
            
            # Flag late night transactions (1 AM - 5 AM)
            if 'hour' in df_processed.columns:
                df_processed['is_late_night'] = ((df_processed['hour'] >= 1) & 
                                                 (df_processed['hour'] <= 5)).astype(int)
            
            # Handle missing values
            df_processed = df_processed.fillna(0)
            
            logger.info(f"Data preprocessing completed: {len(df_processed)} rows, {len(df_processed.columns)} columns")
            
            return df_processed
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise Exception(f"Data preprocessing failed: {str(e)}")
    
    def get_feature_columns(self):
        """
        Get list of feature columns for model training
        
        Returns:
            list: Column names to use as features
        """
        feature_cols = [
            'amount', 'amount_log', 'amount_rounded',
            'hour', 'day_of_week', 'day_of_month', 'month',
            'merchant_encoded', 'location_encoded',
            'is_large_amount', 'is_small_amount',
            'is_high_risk_location', 'transaction_count',
            'is_late_night'
        ]
        return feature_cols
    
    def prepare_features(self, df):
        """
        Extract feature matrix for model input
        
        Args:
            df (pd.DataFrame): Preprocessed DataFrame
            
        Returns:
            np.ndarray: Feature matrix
        """
        try:
            feature_cols = self.get_feature_columns()
            
            # Select only available feature columns
            available_features = [col for col in feature_cols if col in df.columns]
            
            if not available_features:
                raise Exception("No feature columns available")
            
            X = df[available_features].values
            
            logger.info(f"Feature matrix prepared: shape {X.shape}")
            
            return X
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {str(e)}")
            raise Exception(f"Feature preparation failed: {str(e)}")
    
    def split_features_labels(self, df):
        """
        Split data into features (X) and labels (y) for training
        
        Args:
            df (pd.DataFrame): DataFrame with 'is_fraud' column
            
        Returns:
            tuple: (X, y) feature matrix and labels
        """
        try:
            if 'is_fraud' not in df.columns:
                raise Exception("'is_fraud' column not found in training data")
            
            # Separate features and labels
            y = df['is_fraud'].values
            X = self.prepare_features(df)
            
            logger.info(f"Split data: X shape {X.shape}, y shape {y.shape}")
            logger.info(f"Fraud distribution: {np.sum(y)} frauds, {len(y) - np.sum(y)} legitimate")
            
            return X, y
            
        except Exception as e:
            logger.error(f"Data split failed: {str(e)}")
            raise Exception(f"Data split failed: {str(e)}")
    
    def get_data_statistics(self, df):
        """
        Get statistical summary of the data
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            dict: Statistical summary
        """
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns)
        }
        
        if 'amount' in df.columns:
            stats['amount_stats'] = {
                'mean': float(df['amount'].mean()),
                'median': float(df['amount'].median()),
                'min': float(df['amount'].min()),
                'max': float(df['amount'].max()),
                'std': float(df['amount'].std())
            }
        
        if 'is_fraud' in df.columns:
            fraud_count = int(df['is_fraud'].sum())
            stats['fraud_distribution'] = {
                'fraud_count': fraud_count,
                'legitimate_count': len(df) - fraud_count,
                'fraud_rate': float(fraud_count / len(df) * 100)
            }
        
        return stats