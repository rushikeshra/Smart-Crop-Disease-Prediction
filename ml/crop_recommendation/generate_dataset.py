"""
Dataset Generator for Crop Recommendation
Generates the standard 2,200 sample agronomic dataset based on the published
Indian Council of Agricultural Research (ICAR) and standard Kaggle Crop Recommendation dataset distributions.
Features:
- N (Nitrogen content ratio in soil)
- P (Phosphorus content ratio in soil)
- K (Potassium content ratio in soil)
- temperature (Temperature in degree Celsius)
- humidity (Relative humidity in %)
- ph (pH value of the soil)
- rainfall (Rainfall in mm)
- label (Crop name)
"""

import os
import numpy as np
import pandas as pd

# Define statistical distribution parameters for 22 crops
# [N_mean, N_std, P_mean, P_std, K_mean, K_std, temp_mean, temp_std, hum_mean, hum_std, ph_mean, ph_std, rain_mean, rain_std]
CROP_PROFILES = {
    'rice':        [80, 10, 48, 8, 40, 5, 23.6, 2.5, 82.2, 5.0, 6.4, 0.4, 236.1, 30.0],
    'maize':       [77, 12, 48, 9, 20, 4, 22.3, 3.2, 65.0, 7.0, 6.2, 0.4, 84.7, 15.0],
    'chickpea':    [40, 8, 68, 7, 79, 6, 18.8, 1.8, 16.8, 2.5, 7.3, 0.4, 80.0, 10.0],
    'kidneybeans': [20, 6, 67, 7, 20, 3, 20.1, 2.0, 21.6, 3.0, 5.7, 0.3, 105.9, 20.0],
    'pigeonpeas':  [20, 6, 67, 7, 20, 3, 27.7, 2.5, 48.0, 6.0, 5.7, 0.5, 149.4, 25.0],
    'mothbeans':   [21, 6, 48, 6, 20, 3, 28.1, 2.5, 53.1, 6.0, 6.8, 0.5, 51.1, 10.0],
    'mungbean':    [20, 5, 47, 6, 20, 3, 28.5, 2.2, 85.9, 4.0, 6.7, 0.4, 48.4, 9.0],
    'blackgram':   [40, 7, 67, 7, 19, 3, 29.9, 2.2, 65.1, 5.0, 7.1, 0.3, 67.8, 8.0],
    'lentil':      [18, 5, 68, 7, 19, 3, 24.5, 2.5, 64.8, 5.0, 6.9, 0.4, 45.6, 8.0],
    'pomegranate': [18, 5, 18, 4, 40, 4, 21.8, 2.5, 90.1, 3.0, 6.4, 0.4, 107.5, 12.0],
    'banana':      [100, 10, 82, 8, 50, 5, 27.3, 2.0, 80.3, 4.0, 5.9, 0.4, 104.6, 12.0],
    'mango':       [20, 5, 27, 4, 30, 4, 31.2, 2.5, 50.1, 5.0, 5.7, 0.5, 94.7, 12.0],
    'grapes':      [23, 6, 132, 9, 200, 10, 23.8, 4.0, 81.8, 3.0, 6.0, 0.3, 69.6, 10.0],
    'watermelon':  [99, 10, 17, 4, 50, 5, 25.5, 2.5, 85.1, 4.0, 6.5, 0.4, 50.7, 8.0],
    'muskmelon':   [100, 10, 17, 4, 50, 5, 28.6, 2.0, 92.3, 3.0, 6.3, 0.3, 24.6, 4.0],
    'apple':       [20, 5, 134, 10, 199, 10, 22.6, 2.0, 92.3, 3.0, 5.9, 0.4, 112.6, 15.0],
    'orange':      [19, 5, 16, 4, 10, 2, 22.7, 4.0, 92.1, 3.0, 7.0, 0.4, 110.4, 15.0],
    'papaya':      [49, 8, 59, 7, 50, 5, 33.7, 3.0, 92.4, 3.0, 6.7, 0.4, 142.6, 20.0],
    'coconut':     [21, 6, 17, 4, 30, 4, 27.4, 2.0, 94.8, 3.0, 5.9, 0.3, 175.6, 25.0],
    'cotton':      [117, 10, 46, 6, 19, 3, 23.9, 2.0, 79.8, 4.0, 6.9, 0.4, 80.3, 10.0],
    'jute':        [78, 10, 46, 6, 39, 4, 24.9, 2.0, 79.6, 5.0, 6.7, 0.4, 174.7, 20.0],
    'coffee':      [101, 10, 28, 5, 29, 4, 25.5, 2.0, 58.8, 5.0, 6.7, 0.4, 158.0, 25.0]
}

def generate_crop_dataset(output_path, samples_per_crop=100, random_state=42):
    np.random.seed(random_state)
    rows = []
    
    for crop, params in CROP_PROFILES.items():
        (n_m, n_s, p_m, p_s, k_m, k_s, t_m, t_s, h_m, h_s, ph_m, ph_s, r_m, r_s) = params
        
        N = np.clip(np.random.normal(n_m, n_s, samples_per_crop), 0, 150)
        P = np.clip(np.random.normal(p_m, p_s, samples_per_crop), 5, 150)
        K = np.clip(np.random.normal(k_m, k_s, samples_per_crop), 5, 210)
        temp = np.clip(np.random.normal(t_m, t_s, samples_per_crop), 8.0, 45.0)
        hum = np.clip(np.random.normal(h_m, h_s, samples_per_crop), 10.0, 100.0)
        ph = np.clip(np.random.normal(ph_m, ph_s, samples_per_crop), 3.5, 9.9)
        rain = np.clip(np.random.normal(r_m, r_s, samples_per_crop), 20.0, 300.0)
        
        for i in range(samples_per_crop):
            rows.append({
                'N': round(float(N[i]), 2),
                'P': round(float(P[i]), 2),
                'K': round(float(K[i]), 2),
                'temperature': round(float(temp[i]), 2),
                'humidity': round(float(hum[i]), 2),
                'ph': round(float(ph[i]), 2),
                'rainfall': round(float(rain[i]), 2),
                'label': crop
            })
            
    df = pd.DataFrame(rows)
    # Shuffle
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully at {output_path} with {len(df)} rows and {df['label'].nunique()} crops.")
    return df

if __name__ == '__main__':
    dest = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'crop_recommendation', 'crop_recommendation.csv'))
    generate_crop_dataset(dest)
