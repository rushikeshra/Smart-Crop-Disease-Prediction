"""
Crop Recommendation Preprocessing Module
Handles data loading, validation of agronomic limits, and feature scaling.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

# Agronomic physical limits for validation
FEATURE_LIMITS = {
    'N': {'min': 0, 'max': 140, 'unit': 'ratio in soil (kg/ha equivalent)', 'desc': 'Nitrogen'},
    'P': {'min': 5, 'max': 145, 'unit': 'ratio in soil (kg/ha equivalent)', 'desc': 'Phosphorus'},
    'K': {'min': 5, 'max': 205, 'unit': 'ratio in soil (kg/ha equivalent)', 'desc': 'Potassium'},
    'temperature': {'min': 8.0, 'max': 45.0, 'unit': '°C', 'desc': 'Temperature'},
    'humidity': {'min': 14.0, 'max': 100.0, 'unit': '%', 'desc': 'Humidity'},
    'ph': {'min': 3.5, 'max': 9.9, 'unit': 'pH (0-14)', 'desc': 'Soil pH'},
    'rainfall': {'min': 20.0, 'max': 300.0, 'unit': 'mm', 'desc': 'Rainfall'}
}

def validate_input(n, p, k, temp, humidity, ph, rainfall):
    """
    Validates input parameters against physiological agricultural limits.
    Returns: (is_valid: bool, error_message: str, cleaned_values: dict)
    """
    inputs = {
        'N': n,
        'P': p,
        'K': k,
        'temperature': temp,
        'humidity': humidity,
        'ph': ph,
        'rainfall': rainfall
    }
    cleaned = {}
    
    for key, value in inputs.items():
        if value is None:
            return False, f"Missing required parameter: {key} ({FEATURE_LIMITS[key]['desc']})", {}
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            return False, f"Invalid numeric value for {key}: {value}", {}
            
        limits = FEATURE_LIMITS[key]
        if val_float < limits['min'] or val_float > limits['max']:
            return False, (
                f"Parameter '{key}' ({limits['desc']}) value {val_float} is outside realistic agricultural limits "
                f"[{limits['min']} - {limits['max']} {limits['unit']}]."
            ), {}
        cleaned[key] = val_float
        
    return True, "", cleaned

def create_feature_vector(cleaned_values):
    """
    Converts a dictionary of cleaned features into a 2D numpy array shaped (1, 7).
    """
    return np.array([[
        cleaned_values['N'],
        cleaned_values['P'],
        cleaned_values['K'],
        cleaned_values['temperature'],
        cleaned_values['humidity'],
        cleaned_values['ph'],
        cleaned_values['rainfall']
    ]])
