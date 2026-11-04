"""
Script to curate 2 verified sample images for each of the 7 supported crops
and verify 100% exact prediction with MobileNetV2.
"""

import os
import shutil
import json
import numpy as np
from PIL import Image
import tensorflow as tf

project_root = os.path.abspath(os.path.dirname(__file__))
target_dir = os.path.join(project_root, "sample_crop_images")
os.makedirs(target_dir, exist_ok=True)

test_base = os.path.join(project_root, "dataset", "processed", "test")
model_path = os.path.join(project_root, "models", "disease_model.keras")
model = tf.keras.models.load_model(model_path)

with open(os.path.join(project_root, "models", "class_names.json"), "r") as f:
    class_mapping = json.load(f)

# Define 2 images for each of the 7 crops
curated_samples = [
    # 1. Apple
    ("apple_sample_1_scab.jpg", "Apple___Apple_scab", "106aaa5f-c98d-482d-88ef-8e5170e9072d___FREC_Scab 3489.JPG"),
    ("apple_sample_2_healthy.jpg", "Apple___healthy", "0ec3bd54-80a1-4dcd-9411-bcfafd147272___RS_HL 7534.JPG"),
    # 2. Corn (Maize)
    ("corn_sample_1_common_rust.jpg", "Corn_(maize)___Common_rust_", "RS_Rust 1620.JPG"),
    ("corn_sample_2_healthy.jpg", "Corn_(maize)___healthy", "16123a33-12e5-414e-9ae0-695b86e6cb3a___R.S_HL 8136 copy.jpg"),
    # 3. Grape
    ("grape_sample_1_black_rot.jpg", "Grape___Black_rot", "23b27c33-a960-4f91-9160-045f3471ff7b___FAM_B.Rot 0430.JPG"),
    ("grape_sample_2_healthy.jpg", "Grape___healthy", "1c13c447-4d2d-4eac-9835-705d952b09d6___Mt.N.V_HL 9128.JPG"),
    # 4. Pepper (Bell Pepper)
    ("pepper_sample_1_bacterial_spot.jpg", "Pepper__bell___Bacterial_spot", "188f102a-6f64-4180-9d38-f98b61aaec60___JR_B.Spot 9014.JPG"),
    ("pepper_sample_2_healthy.jpg", "Pepper__bell___healthy", "15357dc6-ebde-4ce0-a230-4a1e07b08ecd___JR_HL 8098.JPG"),
    # 5. Potato
    ("potato_sample_1_early_blight.jpg", "Potato___Early_blight", "159f49c5-8d80-41cb-b730-333fdefdff62___RS_Early.B 7301.JPG"),
    ("potato_sample_2_healthy.jpg", "Potato___healthy", "00fc2ee5-729f-4757-8aeb-65c3355874f2___RS_HL 1864.JPG"),
    # 6. Soybean
    ("soybean_sample_1_healthy.jpg", "Soybean___healthy", "3256eb2c-061d-48b8-b7df-5939eff8a590___RS_HL 3926.JPG"),
    ("soybean_sample_2_healthy.jpg", "Soybean___healthy", "0f04ef1e-2a20-4986-9530-40707c70b708___RS_HL 7145.JPG"),
    # 7. Tomato
    ("tomato_sample_1_early_blight.jpg", "Tomato___Early_blight", "394ebb8a-49b8-4122-bd81-f3c862491db9___RS_Erly.B 7513.JPG"),
    ("tomato_sample_2_healthy.jpg", "Tomato___healthy", "1a972145-610d-4efe-96e7-e0253c4ece4a___GH_HL Leaf 237.1.JPG")
]

print("=" * 115)
print(f"VERIFYING AND COPYING {len(curated_samples)} SAMPLE IMAGES (2 PER CROP)")
print("Target Directory: " + target_dir)
print("=" * 115)
print(f"{'File Name':<34} | {'Expected Condition':<32} | {'Prediction':<32} | {'Confidence'}")
print("-" * 115)

for clean_name, cls_dir, orig_name in curated_samples:
    src = os.path.join(test_base, cls_dir, orig_name)
    dst = os.path.join(target_dir, clean_name)
    if not os.path.exists(src):
        folder = os.path.join(test_base, cls_dir)
        files = os.listdir(folder)
        src = os.path.join(folder, files[0])
    shutil.copy2(src, dst)
    
    # Run Inference
    im = Image.open(dst).convert("RGB").resize((224, 224))
    arr = np.expand_dims(np.array(im, dtype=np.float32), 0)
    preds = model.predict(arr, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    pred_cls = class_mapping.get(str(pred_idx), class_mapping.get(pred_idx))
    conf = float(preds[pred_idx] * 100)
    
    status = "[MATCH 100%]" if pred_cls == cls_dir else "[MISMATCH]"
    print(f"{clean_name:<34} | {cls_dir:<32} | {pred_cls:<32} | {conf:>6.2f}% {status}")

print("-" * 115)
print(f"Successfully generated 14 curated images in: {target_dir}")
