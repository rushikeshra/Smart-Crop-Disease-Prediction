"""
Verification test script for both active ML models:
1. Crop Recommendation (Random Forest - 22 Crops)
2. Leaf Disease Prediction (MobileNetV2 CNN - 16 Classes)
"""

import os
import sys
import json
import numpy as np
from PIL import Image

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 65)
print("VERIFYING SMART CROP SYSTEM MACHINE LEARNING MODELS")
print("=" * 65)

# -------------------------------------------------------------
# 1. CROP RECOMMENDATION MODEL (Random Forest)
# -------------------------------------------------------------
print("\n[1/2] TESTING CROP RECOMMENDATION MODEL (Random Forest)...")
from ml.crop_recommendation.predict import get_recommender

recommender = get_recommender()
assert recommender.model is not None, "Failed to load Random Forest model!"
assert len(recommender.model.classes_) == 22, f"Expected 22 crop classes, found {len(recommender.model.classes_)}"

sample_soil = {'n': 90, 'p': 42, 'k': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9}
crop_res = recommender.predict(**sample_soil)

print(f"  * Status:           {'SUCCESS' if crop_res['success'] else 'FAILED'}")
print(f"  * Recommended Crop: {crop_res['recommended_crop']}")
print(f"  * Confidence:       {crop_res['confidence']:.2f}%")
print(f"  * Top Suggestions:  {crop_res['top_recommendations']}")
assert crop_res['success'] is True, "Crop recommendation inference failed!"
assert crop_res['recommended_crop'] == 'rice', f"Expected rice, got {crop_res['recommended_crop']}"
print("[PASS] Crop Recommendation Model verified successfully.")

# -------------------------------------------------------------
# 2. DISEASE PREDICTION MODEL (MobileNetV2 CNN)
# -------------------------------------------------------------
print("\n[2/2] TESTING LEAF DISEASE PREDICTION MODEL (MobileNetV2 CNN)...")
from app import load_ml_model, allowed_file

model, class_names = load_ml_model()
assert model is not None, "Failed to load MobileNetV2 model!"
assert len(class_names) == 16, f"Expected 16 disease classes, found {len(class_names)}"

# Test sample image
sample_img_path = os.path.join(project_root, 'sample_crop_images', 'tomato_sample_1_early_blight.jpg')
if not os.path.exists(sample_img_path):
    sample_img_path = os.path.join(project_root, 'dataset', 'sample_leaves', 'test_tomato_early_blight.jpg')

assert os.path.exists(sample_img_path), f"Sample leaf image not found at: {sample_img_path}"

img = Image.open(sample_img_path).convert("RGB").resize((224, 224))
img_arr = np.expand_dims(np.array(img, dtype=np.float32), axis=0)

preds = model.predict(img_arr, verbose=0)[0]
pred_idx = int(np.argmax(preds))
pred_class = class_names[pred_idx]
pred_conf = float(preds[pred_idx] * 100)

print(f"  * Tested Image:     {os.path.basename(sample_img_path)}")
print(f"  * Diagnosed Class:  {pred_class}")
print(f"  * Confidence:       {pred_conf:.2f}%")
assert pred_class == "Tomato___Early_blight", f"Expected Tomato___Early_blight, got {pred_class}"
assert pred_conf >= 90.0, f"Expected confidence >= 90%, got {pred_conf:.2f}%"
print("[PASS] Leaf Disease Model verified successfully.")

print("\n" + "=" * 65)
print("ALL ML MODELS VERIFIED SUCCESSFULLY: 16-CLASS CNN & 22-CROP RF")
print("=" * 65)
