# Crop Recommendation Machine Learning Module

This module implements an agronomic decision-support model utilizing **Random Forest Classification** to predict the optimal crop for given soil nutrients ($N, P, K$) and environmental factors (Temperature, Humidity, Soil pH, Rainfall).

---

## 1. Feature Specifications

| Feature | Unit / Metric | Physiological Range | Agronomic Significance |
| :--- | :--- | :--- | :--- |
| **N** (Nitrogen) | kg/ha equivalent (ratio) | 0 – 140 | Essential for vegetative growth and chlorophyll synthesis |
| **P** (Phosphorus)| kg/ha equivalent (ratio) | 5 – 145 | Crucial for root development, seed formation, and energy transfer |
| **K** (Potassium) | kg/ha equivalent (ratio) | 5 – 205 | Enhances disease resistance, water retention, and enzyme activation |
| **Temperature** | °C | 8.0 – 45.0 | Governs germination, photosynthesis, and transpiration |
| **Humidity** | % | 14.0 – 100.0 | Affects transpiration rates and disease susceptibility |
| **pH** | Logarithmic scale (0–14) | 3.5 – 9.9 | Determines nutrient solubility and microbial activity |
| **Rainfall** | mm | 20.0 – 300.0 | Primary water supply for rainfed agriculture |

---

## 2. Model Architecture & Hyperparameters

- **Algorithm**: `RandomForestClassifier` (Ensemble of Decorrelated Decision Trees)
- **Number of Estimators**: 100
- **Max Depth**: 16
- **Splitting Criterion**: Gini Impurity ($I_G(p) = 1 - \sum_{i=1}^{J} p_i^2$)
- **Preprocessing**: `StandardScaler` ($\mu=0, \sigma=1$)

---

## 3. How to Train the Model

To retrain the model and regenerate evaluation metrics:

```bash
cd ml/crop_recommendation
python train.py
```

Generated artifacts:
- `model/crop_recommendation_rf.joblib`: Serialized Random Forest Model
- `model/crop_scaler.joblib`: Fitted Feature Scaler
- `model/metrics.json`: Evaluated accuracy, macro F1, and confusion matrix
