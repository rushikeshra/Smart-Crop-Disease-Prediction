"""
Training Pipeline for Crop Recommendation System
Trains a Random Forest Classifier on the 22-class Crop Recommendation dataset.
Evaluates model performance with Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
Serializes model, scaler, and evaluation metrics for deployment.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

from generate_dataset import generate_crop_dataset
from preprocessing import FEATURE_NAMES

def run_training(dataset_path=None, model_dir=None, random_state=42):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if dataset_path is None:
        dataset_path = os.path.abspath(os.path.join(base_dir, '..', '..', 'datasets', 'crop_recommendation', 'crop_recommendation.csv'))
        
    if model_dir is None:
        model_dir = os.path.join(base_dir, 'model')
        
    os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Generating authentic dataset...")
        generate_crop_dataset(dataset_path, samples_per_crop=100, random_state=random_state)
        
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset Shape: {df.shape}")
    print(f"Target distribution:\n{df['label'].value_counts().to_dict()}\n")
    
    X = df[FEATURE_NAMES]
    y = df['label']
    
    # Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    # Feature Scaling (StandardScaler)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=16,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=random_state,
        n_jobs=-1
    )
    
    print("Training Random Forest Classifier...")
    rf_model.fit(X_train_scaled, y_train)
    
    # Model Evaluation on unseen test set
    y_pred = rf_model.predict(X_test_scaled)
    y_pred_proba = rf_model.predict_proba(X_test_scaled)
    
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average='macro')
    rec_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    prec_weighted = precision_score(y_test, y_pred, average='weighted')
    rec_weighted = recall_score(y_test, y_pred, average='weighted')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    clf_report = classification_report(y_test, y_pred, output_dict=True)
    conf_mat = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature importances
    importances = dict(zip(FEATURE_NAMES, [round(float(x), 4) for x in rf_model.feature_importances_]))
    
    metrics = {
        'model_name': 'Random Forest Classifier',
        'n_estimators': 100,
        'train_samples': int(len(X_train)),
        'test_samples': int(len(X_test)),
        'num_classes': int(len(rf_model.classes_)),
        'classes': list(rf_model.classes_),
        'accuracy': round(float(acc), 4),
        'precision_macro': round(float(prec_macro), 4),
        'recall_macro': round(float(rec_macro), 4),
        'f1_macro': round(float(f1_macro), 4),
        'precision_weighted': round(float(prec_weighted), 4),
        'recall_weighted': round(float(rec_weighted), 4),
        'f1_weighted': round(float(f1_weighted), 4),
        'feature_importances': importances,
        'confusion_matrix': conf_mat,
        'classification_report': clf_report
    }
    
    print("\n================= MODEL EVALUATION RESULTS =================")
    print(f"Accuracy:           {acc * 100:.2f}%")
    print(f"Precision (Macro):  {prec_macro * 100:.2f}%")
    print(f"Recall (Macro):     {rec_macro * 100:.2f}%")
    print(f"F1-Score (Macro):   {f1_macro * 100:.2f}%")
    print("\nFeature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {feat:12s}: {imp * 100:6.2f}%")
    print("============================================================\n")
    
    # Save Model Artifacts
    model_path = os.path.join(model_dir, 'crop_recommendation_rf.joblib')
    scaler_path = os.path.join(model_dir, 'crop_scaler.joblib')
    metrics_path = os.path.join(model_dir, 'metrics.json')
    
    joblib.dump(rf_model, model_path)
    joblib.dump(scaler, scaler_path)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Model saved to:   {model_path}")
    print(f"Scaler saved to:  {scaler_path}")
    print(f"Metrics saved to: {metrics_path}")
    
    return metrics

if __name__ == '__main__':
    run_training()
