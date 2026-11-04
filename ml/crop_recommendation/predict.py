"""
Crop Recommendation Prediction Module
Loads trained Random Forest model and standard scaler.
Performs agronomic validation, feature transformation, inference, and confidence scoring.
"""

import os
import joblib
import numpy as np
import pandas as pd

try:
    from .preprocessing import validate_input, create_feature_vector, FEATURE_LIMITS, FEATURE_NAMES
except ImportError:
    from preprocessing import validate_input, create_feature_vector, FEATURE_LIMITS, FEATURE_NAMES

class CropRecommender:
    def __init__(self, model_path=None, scaler_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if model_path is None:
            model_path = os.path.join(base_dir, 'model', 'crop_recommendation_rf.joblib')
        if scaler_path is None:
            scaler_path = os.path.join(base_dir, 'model', 'crop_scaler.joblib')
            
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self._load_model()
        
    def _load_model(self):
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            print("Trained model files not found. Auto-training Random Forest model...")
            from train import run_training
            run_training()
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        print(f"Loaded CropRecommender model with {len(self.model.classes_)} crop classes.")
        
    def predict(self, n, p, k, temperature, humidity, ph, rainfall):
        """
        Runs crop recommendation prediction.
        Returns dict:
        {
            'success': bool,
            'recommended_crop': str,
            'confidence': float (0-100),
            'top_recommendations': list of {'crop': str, 'confidence': float},
            'inputs': dict,
            'error': str (if failed)
        }
        """
        is_valid, err_msg, cleaned_inputs = validate_input(n, p, k, temperature, humidity, ph, rainfall)
        if not is_valid:
            return {
                'success': False,
                'error': err_msg,
                'recommended_crop': None,
                'confidence': 0.0,
                'top_recommendations': [],
                'inputs': {
                    'N': n, 'P': p, 'K': k,
                    'temperature': temperature, 'humidity': humidity,
                    'ph': ph, 'rainfall': rainfall
                }
            }
            
        feat_df = pd.DataFrame([cleaned_inputs], columns=FEATURE_NAMES)
        scaled_feat = self.scaler.transform(feat_df)
        
        # Predict class & class probabilities
        probabilities = self.model.predict_proba(scaled_feat)[0]
        classes = self.model.classes_
        
        # Sort by confidence descending
        top_indices = np.argsort(probabilities)[::-1]
        
        top_recommendations = []
        for idx in top_indices[:3]:
            crop_name = str(classes[idx])
            conf_pct = round(float(probabilities[idx]) * 100, 2)
            top_recommendations.append({
                'crop': crop_name,
                'confidence': conf_pct
            })
            
        recommended_crop = top_recommendations[0]['crop']
        primary_confidence = top_recommendations[0]['confidence']
        
        return {
            'success': True,
            'recommended_crop': recommended_crop,
            'confidence': primary_confidence,
            'top_recommendations': top_recommendations,
            'inputs': cleaned_inputs,
            'error': None
        }

# Singleton instance
_recommender_instance = None

def get_recommender():
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = CropRecommender()
    return _recommender_instance

if __name__ == '__main__':
    recommender = get_recommender()
    # Test with standard Rice soil profile: N=90, P=42, K=43, temp=20.8, hum=82.0, ph=6.5, rain=202.9
    res = recommender.predict(90, 42, 43, 20.8, 82.0, 6.5, 202.9)
    print("Test Prediction Output:", res)
