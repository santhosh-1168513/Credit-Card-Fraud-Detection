"""
Fraud Detector Module
Main fraud detection logic and workflow management
"""

import logging
import numpy as np
from src.data_processor import DataProcessor

logger = logging.getLogger(__name__)


class FraudDetector:
    """
    Main fraud detection class that orchestrates the detection workflow
    """
    
    def __init__(self, model_manager):
        """
        Initialize FraudDetector
        
        Args:
            model_manager: ModelManager instance
        """
        self.model_manager = model_manager
        self.data_processor = DataProcessor()
        self.prediction_count = 0
        logger.info("FraudDetector initialized")
    
    def train(self, df):
        """
        Train fraud detection model
        
        Args:
            df (pd.DataFrame): Training data with 'is_fraud' labels
            
        Returns:
            dict: Training results
        """
        try:
            logger.info("Starting fraud detection model training...")
            
            # Validate data
            validation_result = self.data_processor.validate_data(df)
            if not validation_result['valid']:
                raise Exception(f"Invalid data: {validation_result['errors']}")
            
            # Preprocess data
            df_processed = self.data_processor.preprocess_data(df)
            
            # Split features and labels
            X, y = self.data_processor.split_features_labels(df_processed)
            
            # Train model
            training_results = self.model_manager.train_model(X, y)
            
            # Save model
            if training_results['success']:
                self.model_manager.save_model()
                logger.info("Model saved successfully")
            
            # Get data statistics
            data_stats = self.data_processor.get_data_statistics(df)
            
            return {
                'success': True,
                'message': 'Model trained successfully',
                'metrics': training_results['metrics'],
                'model_info': training_results['model_info'],
                'data_statistics': data_stats
            }
            
        except Exception as e:
            logger.error(f"Training workflow failed: {str(e)}")
            raise Exception(f"Training failed: {str(e)}")
    
    def predict(self, df):
        """
        Perform fraud detection on transactions
        
        Args:
            df (pd.DataFrame): Transaction data
            
        Returns:
            dict: Fraud detection results
        """
        try:
            logger.info(f"Starting fraud detection for {len(df)} transactions...")
            
            # Validate data
            validation_result = self.data_processor.validate_data(df)
            if not validation_result['valid']:
                raise Exception(f"Invalid data: {validation_result['errors']}")
            
            # Preprocess data
            df_processed = self.data_processor.preprocess_data(df)
            
            # Prepare features
            X = self.data_processor.prepare_features(df_processed)
            
            # Make predictions
            prediction_results = self.model_manager.predict(X)
            
            # Process results
            results = self._process_predictions(df, prediction_results)
            
            # Update prediction counter
            self.prediction_count += len(df)
            
            logger.info(f"Fraud detection completed: {results['summary']['fraud_count']} frauds detected")
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction workflow failed: {str(e)}")
            raise Exception(f"Fraud detection failed: {str(e)}")
    
    def _process_predictions(self, df_original, prediction_results):
        """
        Process raw predictions into structured results
        
        Args:
            df_original (pd.DataFrame): Original transaction data
            prediction_results (dict): Raw predictions from model
            
        Returns:
            dict: Formatted results
        """
        predictions = prediction_results['predictions']
        fraud_probabilities = prediction_results['fraud_probability']
        
        # Create results list
        transactions = []
        fraud_count = 0
        legitimate_count = 0
        
        for idx, row in df_original.iterrows():
            is_fraud = int(predictions[idx])
            fraud_prob = float(fraud_probabilities[idx])
            
            # Determine risk level and status
            if fraud_prob >= 0.7:
                status = 'fraud'
                risk_level = 'High'
                fraud_count += 1
            elif fraud_prob >= 0.5:
                status = 'warning'
                risk_level = 'Medium'
                legitimate_count += 1
            else:
                status = 'legitimate'
                risk_level = 'Low'
                legitimate_count += 1
            
            # Generate fraud indicators for high-risk transactions
            indicators = []
            if fraud_prob >= 0.7:
                indicators = self._generate_fraud_indicators(row, fraud_prob)
            
            transaction_result = {
                'transaction_id': str(row.get('transaction_id', f'TXN_{idx}')),
                'amount': float(row.get('amount', 0)),
                'merchant': str(row.get('merchant', 'Unknown')),
                'location': str(row.get('location', 'Unknown')),
                'timestamp': str(row.get('timestamp', '')),
                'card_number': str(row.get('card_number', 'N/A')),
                'is_fraud': is_fraud,
                'fraud_probability': round(fraud_prob * 100, 2),
                'risk_score': round(fraud_prob * 100, 2),
                'risk_level': risk_level,
                'status': status,
                'indicators': indicators
            }
            
            transactions.append(transaction_result)
        
        # Calculate summary statistics
        total_transactions = len(predictions)
        fraud_rate = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
        
        summary = {
            'total_transactions': total_transactions,
            'fraud_count': fraud_count,
            'legitimate_count': legitimate_count,
            'fraud_rate': round(fraud_rate, 2),
            'average_fraud_probability': round(float(np.mean(fraud_probabilities) * 100), 2),
            'max_fraud_probability': round(float(np.max(fraud_probabilities) * 100), 2),
            'min_fraud_probability': round(float(np.min(fraud_probabilities) * 100), 2)
        }
        
        return {
            'summary': summary,
            'transactions': transactions,
            'model_info': self.model_manager.get_model_info()
        }
    
    def _generate_fraud_indicators(self, transaction, fraud_prob):
        """
        Generate fraud indicators based on transaction characteristics
        
        Args:
            transaction: Transaction data
            fraud_prob (float): Fraud probability
            
        Returns:
            list: List of fraud indicators
        """
        indicators = []
        
        amount = float(transaction.get('amount', 0))
        location = str(transaction.get('location', ''))
        
        # Amount-based indicators
        if amount > 5000:
            indicators.append('Unusually high transaction amount')
        elif amount < 10:
            indicators.append('Suspiciously low transaction amount')
        
        # Location-based indicators
        high_risk_locations = ['Nigeria', 'Russia', 'Ukraine', 'Unknown']
        if any(loc in location for loc in high_risk_locations):
            indicators.append('Transaction from high-risk location')
        
        # Time-based indicators
        try:
            import pandas as pd
            timestamp = pd.to_datetime(transaction.get('timestamp'))
            hour = timestamp.hour
            
            if 1 <= hour <= 5:
                indicators.append('Transaction during unusual hours (1 AM - 5 AM)')
        except:
            pass
        
        # High confidence indicator
        if fraud_prob > 0.9:
            indicators.append('Very high fraud probability score')
        
        # Generic indicators based on probability
        if fraud_prob >= 0.8:
            indicators.append('Multiple fraud patterns detected')
            indicators.append('Transaction flagged by ML model with high confidence')
        
        return indicators[:5]  # Return top 5 indicators
    
    def get_prediction_count(self):
        """
        Get total number of predictions made
        
        Returns:
            int: Prediction count
        """
        return self.prediction_count
    
    def reset_prediction_count(self):
        """Reset prediction counter"""
        self.prediction_count = 0
        logger.info("Prediction counter reset")