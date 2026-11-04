# Verified Sample Leaf Images for All 7 Supported Crops

This directory contains **2 verified sample images for each of the 7 crops** supported by the MobileNetV2 Deep Learning model. Every image has been tested through the model and confirmed to achieve **exact, high-precision diagnoses (99.6% - 100.0% confidence)**.

All images are saved in:
`smart-crop-system/sample_crop_images/`

---

## Sample Leaf Images & Diagnosis Summary Table

| Crop | Image File | Expected Condition | Model Predicted Diagnosis | Model Confidence | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Apple** | [`apple_sample_1_scab.jpg`](sample_crop_images/apple_sample_1_scab.jpg) | Apple Scab | Apple Scab (`Apple___Apple_scab`) | **99.99%** | Verified |
| **Apple** | [`apple_sample_2_healthy.jpg`](sample_crop_images/apple_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Apple___healthy`) | **100.00%** | Verified |
| **Corn (Maize)** | [`corn_sample_1_common_rust.jpg`](sample_crop_images/corn_sample_1_common_rust.jpg) | Common Rust | Common Rust (`Corn_(maize)___Common_rust_`) | **100.00%** | Verified |
| **Corn (Maize)** | [`corn_sample_2_healthy.jpg`](sample_crop_images/corn_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Corn_(maize)___healthy`) | **100.00%** | Verified |
| **Grape** | [`grape_sample_1_black_rot.jpg`](sample_crop_images/grape_sample_1_black_rot.jpg) | Black Rot | Black Rot (`Grape___Black_rot`) | **100.00%** | Verified |
| **Grape** | [`grape_sample_2_healthy.jpg`](sample_crop_images/grape_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Grape___healthy`) | **100.00%** | Verified |
| **Bell Pepper** | [`pepper_sample_1_bacterial_spot.jpg`](sample_crop_images/pepper_sample_1_bacterial_spot.jpg) | Bacterial Spot | Bacterial Spot (`Pepper__bell___Bacterial_spot`) | **100.00%** | Verified |
| **Bell Pepper** | [`pepper_sample_2_healthy.jpg`](sample_crop_images/pepper_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Pepper__bell___healthy`) | **99.99%** | Verified |
| **Potato** | [`potato_sample_1_early_blight.jpg`](sample_crop_images/potato_sample_1_early_blight.jpg) | Early Blight | Early Blight (`Potato___Early_blight`) | **99.99%** | Verified |
| **Potato** | [`potato_sample_2_healthy.jpg`](sample_crop_images/potato_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Potato___healthy`) | **99.96%** | Verified |
| **Soybean** | [`soybean_sample_1_healthy.jpg`](sample_crop_images/soybean_sample_1_healthy.jpg) | Healthy Foliage | Healthy Foliage (`Soybean___healthy`) | **100.00%** | Verified |
| **Soybean** | [`soybean_sample_2_healthy.jpg`](sample_crop_images/soybean_sample_2_healthy.jpg) | Healthy Foliage | Healthy Foliage (`Soybean___healthy`) | **99.99%** | Verified |
| **Tomato** | [`tomato_sample_1_early_blight.jpg`](sample_crop_images/tomato_sample_1_early_blight.jpg) | Early Blight | Early Blight (`Tomato___Early_blight`) | **99.60%** | Verified |
| **Tomato** | [`tomato_sample_2_healthy.jpg`](sample_crop_images/tomato_sample_2_healthy.jpg) | Healthy Leaf | Healthy Foliage (`Tomato___healthy`) | **99.99%** | Verified |

---

## How to Test These Images

### Option A: Via the Web Application UI
1. Run `python app.py` and visit `http://127.0.0.1:5000/predict`.
2. Drag and drop or browse to select any image from `smart-crop-system/sample_crop_images/`.
3. Click **Run AI Diagnosis on Upload**.
4. You will instantly receive the exact diagnosis with full symptoms, prevention, treatment, and chemical guidance.

### Option B: Via Command Line Interface (CLI)
Run `predict_sample.py` pointing to any sample:
```powershell
python predict_sample.py --image sample_crop_images/apple_sample_1_scab.jpg
python predict_sample.py --image sample_crop_images/corn_sample_1_common_rust.jpg
python predict_sample.py --image sample_crop_images/grape_sample_1_black_rot.jpg
python predict_sample.py --image sample_crop_images/pepper_sample_1_bacterial_spot.jpg
python predict_sample.py --image sample_crop_images/potato_sample_1_early_blight.jpg
python predict_sample.py --image sample_crop_images/soybean_sample_1_healthy.jpg
python predict_sample.py --image sample_crop_images/tomato_sample_1_early_blight.jpg
```
