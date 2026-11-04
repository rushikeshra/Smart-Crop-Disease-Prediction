"""
Quick Model Inference Runner
Run single-image or directory diagnosis with the trained MobileNetV2 model.
Usage:
    python predict_sample.py
    python predict_sample.py --image path/to/leaf.jpg
    python predict_sample.py --soybean
"""

import os
import sys
import json
import argparse
import numpy as np
from PIL import Image

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def load_resources():
    import tensorflow as tf
    model_path = os.path.join(project_root, "models", "disease_model.keras")
    mapping_path = os.path.join(project_root, "models", "class_names.json")
    info_path = os.path.join(project_root, "database", "disease_info.json")

    if not os.path.exists(model_path):
        model_path = model_path.replace(".keras", ".h5")

    print(f"[1/3] Loading trained model from: {model_path}")
    model = tf.keras.models.load_model(model_path)

    print(f"[2/3] Loading class mapping from: {mapping_path}")
    with open(mapping_path, "r", encoding="utf-8") as f:
        class_mapping = json.load(f)

    print(f"[3/3] Loading disease knowledge base from: {info_path}")
    disease_info = {}
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            disease_info = json.load(f)

    return model, class_mapping, disease_info

def run_prediction(image_path, model, class_mapping, disease_info):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return

    print("\n" + "=" * 65)
    print(f"DIAGNOSING LEAF: {os.path.basename(image_path)}")
    print("=" * 65)

    img = Image.open(image_path).convert("RGB")
    orig_w, orig_h = img.size
    img_resized = img.resize((224, 224))
    img_array = np.expand_dims(np.array(img_resized), axis=0)

    preds = model.predict(img_array, verbose=0)[0]
    top_indices = np.argsort(preds)[::-1][:3]

    top_idx = top_indices[0]
    top_class = class_mapping.get(str(top_idx), class_mapping.get(top_idx, "Unknown"))
    top_conf = preds[top_idx] * 100

    info = disease_info.get(top_class, {})
    crop_name = info.get("crop_name", top_class.split("___")[0].replace("_", " "))
    disease_name = info.get("disease_name", top_class.split("___")[1].replace("_", " "))

    print(f"\n[RESULT]")
    print(f"  * Predicted Class: {top_class}")
    print(f"  * Crop:            {crop_name}")
    print(f"  * Diagnosis:       {disease_name}")
    print(f"  * Confidence:      {top_conf:.2f}%")

    translations = info.get("translations", {})
    if translations:
        hi_trans = translations.get("hi", {})
        mr_trans = translations.get("mr", {})
        print(f"\n[MULTILINGUAL OUTPUT / बहुभाषी परिणाम]")
        print(f"  * [English] Crop: {crop_name} | Disease: {disease_name}")
        if hi_trans:
            print(f"  * [हिंदी]    फसल: {hi_trans.get('crop_name', crop_name)} | रोग: {hi_trans.get('disease_name', disease_name)}")
        if mr_trans:
            print(f"  * [मराठी]    पीक: {mr_trans.get('crop_name', crop_name)} | रोग: {mr_trans.get('disease_name', disease_name)}")

    print(f"\n[TOP 3 PREDICTIONS]")
    for rank, idx in enumerate(top_indices, start=1):
        cls_name = class_mapping.get(str(idx), class_mapping.get(idx))
        print(f"  {rank}. {cls_name:<38} {preds[idx]*100:>6.2f}%")

    if info:
        print(f"\n[ADVISORY INFORMATION]")
        if "description" in info:
            print(f"  * Description: {info['description'][:140]}...")
        if "prevention" in info and info["prevention"]:
            print(f"  * Prevention:  {info['prevention'][0]}")
        if "treatment_or_cure" in info and info["treatment_or_cure"]:
            print(f"  * Treatment:   {info['treatment_or_cure'][0]}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Run inference with the trained MobileNetV2 model")
    parser.add_argument("--image", type=str, default=None, help="Path to leaf image file")
    parser.add_argument("--soybean", action="store_true", help="Run on a sample Soybean leaf")
    args = parser.parse_args()

    model, class_mapping, disease_info = load_resources()

    if args.image:
        run_prediction(args.image, model, class_mapping, disease_info)
    elif args.soybean:
        soy_dir = os.path.join(project_root, "dataset", "processed", "test", "Soybean___healthy")
        if os.path.exists(soy_dir) and os.listdir(soy_dir):
            sample = os.path.join(soy_dir, os.listdir(soy_dir)[0])
            run_prediction(sample, model, class_mapping, disease_info)
        else:
            print("[ERROR] Soybean test directory empty or not found.")
    else:
        # Default: Run on 2 demo leaves (Soybean + Tomato)
        soy_dir = os.path.join(project_root, "dataset", "processed", "test", "Soybean___healthy")
        if os.path.exists(soy_dir) and os.listdir(soy_dir):
            sample_soy = os.path.join(soy_dir, os.listdir(soy_dir)[0])
            run_prediction(sample_soy, model, class_mapping, disease_info)

        sample_leaves_dir = os.path.join(project_root, "dataset", "sample_leaves")
        sample_tomato = os.path.join(sample_leaves_dir, "test_tomato_early_blight.jpg")
        if not os.path.exists(sample_tomato):
            sample_tomato = os.path.join(sample_leaves_dir, "sample_tomato_early_blight.jpg")
        if os.path.exists(sample_tomato):
            run_prediction(sample_tomato, model, class_mapping, disease_info)

if __name__ == "__main__":
    main()
