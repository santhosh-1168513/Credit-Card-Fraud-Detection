"""
Model Manager Module
Handles machine learning model training, loading, saving, and prediction
"""

import os
import pickle
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import numpy as np

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages machine learning models for fraud detection
    """

    def __init__(self, model_dir='models'):
        """
        Initialize ModelManager

        Args:
            model_dir (str): Directory to save/load models
        """
        self.model_dir = model_dir
        self.model = None
        self.model_info = {
            'type': None,
            'trained_at': None,
            'accuracy': None,
            'precision': None,
            'recall': None,
            'f1_score': None,
            'roc_auc': None
        }

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"ModelManager initialized with directory: {model_dir}")

    def train_model(self, X, y, model_type='random_forest', test_size=0.2):
        """
        Train a machine learning model

        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Labels
            model_type (str): Type of model to train
            test_size (float): Test set size

        Returns:
            dict: Training results
        """
        try:
            logger.info(f"Training {model_type} model with {len(X)} samples")

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            # Initialize model
            if model_type == 'random_forest':
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            elif model_type == 'logistic_regression':
                self.model = LogisticRegression(
                    random_state=42,
                    max_iter=1000
                )
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            # Train model
            self.model.fit(X_train, y_train)

            # Make predictions on test set
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_pred_proba)

            # Update model info
            self.model_info.update({
                'type': model_type,
                'trained_at': str(pd.Timestamp.now()),
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(roc_auc),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            })

            logger.info(f"Model trained successfully. Accuracy: {accuracy:.4f}")

            return {
                'success': True,
                'metrics': {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'roc_auc': roc_auc
                },
                'model_info': self.model_info.copy()
            }

        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def predict(self, X):
        """
        Make predictions using the trained model

        Args:
            X (np.ndarray): Feature matrix

        Returns:
            dict: Prediction results
        """
        try:
            if self.model is None:
                raise Exception("No model loaded. Please train or load a model first.")

            # Make predictions
            predictions = self.model.predict(X)
            fraud_probabilities = self.model.predict_proba(X)[:, 1]

            return {
                'predictions': predictions.tolist(),
                'fraud_probability': fraud_probabilities.tolist()
            }

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise Exception(f"Prediction failed: {str(e)}")

    def save_model(self, filename='fraud_detection_model.pkl'):
        """
        Save the trained model to disk

        Args:
            filename (str): Model filename
        """
        try:
            if self.model is None:
                raise Exception("No model to save")

            filepath = os.path.join(self.model_dir, filename)

            # Save model and info
            model_data = {
                'model': self.model,
                'model_info': self.model_info
            }

            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)

            logger.info(f"Model saved to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise Exception(f"Failed to save model: {str(e)}")

    def load_model(self, filename='fraud_detection_model.pkl'):
        """
        Load a trained model from disk

        Args:
            filename (str): Model filename

        Returns:
            bool: True if loaded successfully
        """
        try:
            filepath = os.path.join(self.model_dir, filename)

            if not os.path.exists(filepath):
                logger.warning(f"Model file not found: {filepath}")
                return False

            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.model_info = model_data['model_info']

            logger.info(f"Model loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False

    def is_model_loaded(self):
        """
        Check if a model is currently loaded

        Returns:
            bool: True if model is loaded
        """
        return self.model is not None

    def get_model_info(self):
        """
        Get information about the current model

        Returns:
            dict: Model information
        """
        if self.model is None:
            return {'status': 'no_model_loaded'}

        return self.model_info.copy()

    def delete_model(self, filename='fraud_detection_model.pkl'):
        """
        Delete a saved model file

        Args:
            filename (str): Model filename to delete
        """
        try:
            filepath = os.path.join(self.model_dir, filename)

            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Model file deleted: {filepath}")
            else:
                logger.warning(f"Model file not found: {filepath}")

        except Exception as e:
            logger.error(f"Failed to delete model: {str(e)}")
            raise Exception(f"Failed to delete model: {str(e)}")
