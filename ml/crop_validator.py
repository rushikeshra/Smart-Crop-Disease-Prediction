import os
import sys
import json
import numpy as np
from PIL import Image
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mapping from internal crop names to human-readable names and their supported disease classes
SUPPORTED_CROPS_INFO = {
    "Apple": {
        "display_name": "Apple",
        "scientific_name": "Malus domestica",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy"],
        "diseases": ["Apple Scab", "Black Rot", "Healthy Foliage"]
    },
    "Bell_Pepper": {
        "display_name": "Bell Pepper (Capsicum)",
        "scientific_name": "Capsicum annuum",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Pepper__bell___Bacterial_spot", "Pepper__bell___healthy"],
        "diseases": ["Bacterial Spot", "Healthy Foliage"]
    },
    "Corn": {
        "display_name": "Corn (Maize)",
        "scientific_name": "Zea mays",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Corn_(maize)___Common_rust_", "Corn_(maize)___healthy"],
        "diseases": ["Common Rust", "Healthy Foliage"]
    },
    "Grape": {
        "display_name": "Grape",
        "scientific_name": "Vitis vinifera",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Grape___Black_rot", "Grape___healthy"],
        "diseases": ["Black Rot", "Healthy Foliage"]
    },
    "Potato": {
        "display_name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"],
        "diseases": ["Early Blight", "Late Blight", "Healthy Foliage"]
    },
    "Tomato": {
        "display_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": ["Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"],
        "diseases": ["Early Blight", "Late Blight", "Healthy Foliage"]
    },
    "Soybean": {
        "display_name": "Soybean",
        "scientific_name": "Glycine max",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": [
            "Soybean___Bacterial_blight",
            "Soybean___Frogeye_leaf_spot",
            "Soybean___Soybean_rust",
            "Soybean___healthy"
        ],
        "diseases": [
            "Bacterial Blight",
            "Frogeye Leaf Spot",
            "Soybean Rust",
            "Healthy Foliage"
        ]
    },
    "Green_Gram": {
        "display_name": "Green Gram (Vigna radiata)",
        "scientific_name": "Vigna radiata",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": [
            "Green_Gram___Cercospora_leaf_spot",
            "Green_Gram___Yellow_mosaic",
            "Green_Gram___Powdery_mildew",
            "Green_Gram___healthy"
        ],
        "diseases": [
            "Cercospora Leaf Spot",
            "Yellow Mosaic Virus",
            "Powdery Mildew",
            "Healthy Foliage"
        ]
    },
    "Cotton": {
        "display_name": "Cotton (Gossypium spp.)",
        "scientific_name": "Gossypium spp.",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": [
            "Cotton___Bacterial_blight",
            "Cotton___Leaf_curl_virus",
            "Cotton___Alternaria_leaf_spot",
            "Cotton___healthy"
        ],
        "diseases": [
            "Bacterial Blight",
            "Leaf Curl Virus",
            "Alternaria Leaf Spot",
            "Healthy Foliage"
        ]
    },
    "Pigeon_Pea": {
        "display_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "scientific_name": "Cajanus cajan",
        "supports_disease": True,
        "model_trained": True,
        "disease_classes": [
            "Pigeon_Pea___Sterility_mosaic",
            "Pigeon_Pea___Phytophthora_blight",
            "Pigeon_Pea___Cercospora_leaf_spot",
            "Pigeon_Pea___healthy"
        ],
        "diseases": [
            "Sterility Mosaic",
            "Phytophthora Blight",
            "Cercospora Leaf Spot",
            "Healthy Foliage"
        ]
    }
}

class CropSystemValidator:
    _instance = None

    def __init__(self):
        self.crop_model = None
        self.crop_feat_extractor = None
        self.crop_classes = None
        self.crop_centroids = None
        self.disease_model = None
        self.disease_feat_extractor = None
        self.disease_classes = None
        self.disease_info = None
        self.load_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CropSystemValidator()
        return cls._instance

    def load_models(self):
        models_dir = os.path.join(BASE_DIR, "models")
        
        # 1. Load Crop Classifier (try .keras, fallback to .h5)
        crop_candidates = [
            os.path.join(models_dir, "crop_model.keras"),
            os.path.join(models_dir, "crop_model_best.h5")
        ]
        for candidate_path in crop_candidates:
            if os.path.exists(candidate_path):
                try:
                    self.crop_model = tf.keras.models.load_model(candidate_path, compile=False)
                    # Feature extractor from crop_features layer
                    try:
                        self.crop_feat_extractor = tf.keras.Model(
                            inputs=self.crop_model.input,
                            outputs=self.crop_model.get_layer("crop_features").output
                        )
                    except Exception:
                        self.crop_feat_extractor = None
                    print(f"[ML SUCCESS] Crop Classifier model loaded from {os.path.basename(candidate_path)}.")
                    break
                except Exception as e:
                    print(f"[ML WARNING] Could not load crop model from {os.path.basename(candidate_path)}: {e}")

        # Crop classes
        classes_path = os.path.join(models_dir, "crop_classes.json")
        if os.path.exists(classes_path):
            try:
                with open(classes_path, "r", encoding="utf-8") as f:
                    self.crop_classes = json.load(f)
            except Exception as e:
                print(f"[ML ERROR] Failed to load crop classes: {e}")

        # Crop centroids & OOD thresholds
        centroids_path = os.path.join(models_dir, "crop_centroids.json")
        if os.path.exists(centroids_path):
            try:
                with open(centroids_path, "r", encoding="utf-8") as f:
                    self.crop_centroids = json.load(f)
            except Exception as e:
                print(f"[ML ERROR] Failed to load crop centroids: {e}")

        # 2. Load Disease Model (try .keras, fallback to .h5)
        disease_candidates = [
            os.path.join(models_dir, "disease_model.keras"),
            os.path.join(models_dir, "disease_model.h5")
        ]
        for candidate_path in disease_candidates:
            if os.path.exists(candidate_path):
                try:
                    self.disease_model = tf.keras.models.load_model(candidate_path, compile=False)
                    try:
                        self.disease_feat_extractor = tf.keras.Model(
                            inputs=self.disease_model.input,
                            outputs=self.disease_model.get_layer("dense_features").output
                        )
                    except Exception:
                        self.disease_feat_extractor = None
                    print(f"[ML SUCCESS] Disease Model loaded from {os.path.basename(candidate_path)}.")
                    break
                except Exception as e:
                    print(f"[ML WARNING] Failed to load disease model from {os.path.basename(candidate_path)}: {e}")

        # Disease classes
        disease_classes_path = os.path.join(models_dir, "class_names.json")
        if os.path.exists(disease_classes_path):
            try:
                with open(disease_classes_path, "r", encoding="utf-8") as f:
                    raw_mapping = json.load(f)
                if isinstance(raw_mapping, dict):
                    self.disease_classes = [raw_mapping[str(i)] if str(i) in raw_mapping else raw_mapping[i] for i in range(len(raw_mapping))]
                else:
                    self.disease_classes = list(raw_mapping)
            except Exception as e:
                print(f"[ML ERROR] Failed to load disease class names: {e}")

        # Disease Info / Recommendations
        info_path = os.path.join(BASE_DIR, "database", "disease_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    self.disease_info = json.load(f)
            except Exception as e:
                print(f"[ML ERROR] Failed to load disease info: {e}")

    def check_foliar_integrity(self, img_pil):
        """
        Validates whether image contains plant foliage/leaf features.
        Rejects blank, solid color, furniture, human, metallic, or non-vegetation images.
        """
        img_rgb = img_pil.convert("RGB").resize((128, 128))
        arr = np.array(img_rgb, dtype=np.float32)

        # 1. Variance check (detects solid/blank/unclear photos)
        std_dev = float(np.std(arr))
        if std_dev < 14.0:
            return False, "Image appears blank, uniformly colored, or lacks visual detail."

        # 2. Vegetation color index (green leaf, chlorotic yellow leaf, necrotic lesion brown)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        green_foliage = (g > r * 1.04) & (g > b * 1.04) & (g > 30)
        green_ratio = float(np.mean(green_foliage))

        yellow_foliage = (r > 60) & (g > 60) & (r > b * 1.15) & (g > b * 1.15)
        brown_foliage = (r > 38) & (g > 24) & (r > g * 1.04) & (g > b * 1.04) & (r < 215) & (b < 115)
        foliar_coverage = float(np.mean(green_foliage | yellow_foliage | brown_foliage))

        # Real leaves have green chlorophyll tissue; non-leaf objects (wooden desk, concrete, skin, text) have ~0%
        if green_ratio < 0.03:
            return False, "Image does not appear to contain plant leaf foliage (no chlorophyll vegetation detected)."

        if foliar_coverage < 0.08:
            return False, "Image does not appear to contain plant foliage or leaf structures."

        return True, None

    def check_fruit_content(self, img_pil):
        """
        Detects isolated fruit photos (spherical smooth fruit with specular highlight and no vein structures).
        """
        img_rgb = img_pil.convert("RGB").resize((128, 128))
        arr = np.array(img_rgb, dtype=np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        # Check for dominant smooth circular fruit color without leaf vein contrast
        # Red fruit (apple, tomato) or bright yellow/orange fruit
        is_red_fruit = (r > 160) & (r > g * 1.5) & (r > b * 1.5)
        is_orange_fruit = (r > 190) & (g > 100) & (g < 170) & (b < 60)
        fruit_pixel_ratio = float(np.mean(is_red_fruit | is_orange_fruit))

        if fruit_pixel_ratio > 0.40:
            # Check edge gradient variance: fruits have smooth internal gradients, unlike leaves with veins
            gray = np.mean(arr, axis=2)
            grad_x = np.abs(gray[:, 1:] - gray[:, :-1])
            grad_y = np.abs(gray[1:, :] - gray[:-1, :])
            edge_density = float(np.mean(grad_x > 18) + np.mean(grad_y > 18)) / 2.0
            if edge_density < 0.08:
                return True, "The uploaded image appears to contain a fruit rather than a single crop leaf."

        return False, None

    def validate_and_classify_crop(self, img_pil):
        """
        Stage 2: Run Crop Classifier & Centroid-based OOD validation.
        Returns:
          is_supported (bool),
          crop_name (str or None),
          confidence (float or None),
          cosine_sim (float or None),
          reason (str or None)
        """
        if self.crop_model is None or not self.crop_classes:
            return False, None, None, None, "Crop classification model is not available."

        img_resized = img_pil.convert("RGB").resize((224, 224))
        img_arr = np.expand_dims(np.array(img_resized, dtype=np.float32), 0)

        # 1. Extract feature embedding from crop_features layer
        if self.crop_feat_extractor is not None:
            feat = self.crop_feat_extractor.predict(img_arr, verbose=0)[0]
            feat_norm = feat / (np.linalg.norm(feat) + 1e-7)
        else:
            feat_norm = None

        # 2. Get Softmax Crop Probabilities
        preds = self.crop_model.predict(img_arr, verbose=0)[0]
        top_idx = int(np.argmax(preds))
        top_crop = self.crop_classes[top_idx]
        top_prob = float(preds[top_idx])

        # 3. Centroid Cosine Distance Validation
        cosine_sim = None
        if feat_norm is not None and self.crop_centroids and top_crop in self.crop_centroids:
            crop_meta = self.crop_centroids[top_crop]
            if "centroids" in crop_meta:
                # Multi-prototype representation (e.g. laboratory healthy foliage vs natural field canopy)
                sims = [float(np.dot(feat_norm, np.array(c, dtype=np.float32))) for c in crop_meta["centroids"]]
                cosine_sim = max(sims)
            else:
                centroid = np.array(crop_meta["centroid"], dtype=np.float32)
                cosine_sim = float(np.dot(feat_norm, centroid))
            ood_threshold = float(crop_meta.get("ood_threshold", 0.65))
        else:
            ood_threshold = 0.65

        # Check OOD rejection
        # If cosine similarity is too low OR softmax probability is ambiguous across classes
        is_ood = False
        if cosine_sim is not None and cosine_sim < ood_threshold:
            is_ood = True
        elif top_prob < 0.45:
            is_ood = True

        if is_ood:
            return (
                False,
                top_crop,
                top_prob,
                cosine_sim,
                f"Image does not match the visual and structural features of supported crops (similarity: {cosine_sim:.3f} < threshold: {ood_threshold:.3f})."
            )

        return True, top_crop, top_prob, cosine_sim, None

    def diagnose_leaf(self, image_path):
        """
        Full End-to-End Hierarchical Crop-Constrained Diagnosis Pipeline.
        """
        try:
            with Image.open(image_path) as img:
                img_pil = img.copy()
        except Exception as e:
            return {
                "status": "invalid_image",
                "title": "Invalid Image File",
                "message": f"Unable to read or decode image: {e}",
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        # Step A: Image Quality & Foliar Check
        is_foliar, foliar_reason = self.check_foliar_integrity(img_pil)
        if not is_foliar:
            return {
                "status": "invalid_image",
                "title": "Non-Foliar / Invalid Image",
                "message": foliar_reason or "Image does not appear to contain a plant leaf.",
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        # Step B: Fruit Check
        is_fruit, fruit_reason = self.check_fruit_content(img_pil)
        if is_fruit:
            return {
                "status": "invalid_image",
                "title": "Fruit / Non-Leaf Image Detected",
                "message": fruit_reason,
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        # Step C: Supported Crop Validation & OOD Gate
        is_supported_crop, detected_crop, crop_prob, cos_sim, ood_reason = self.validate_and_classify_crop(img_pil)
        if not is_supported_crop:
            return {
                "status": "unsupported_crop",
                "title": "Unsupported Crop",
                "message": "This image does not appear to belong to a crop supported by the current model.",
                "detected_candidate": detected_crop,
                "cosine_similarity": cos_sim,
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        # Step D: Crop-Constrained Disease Classification (All 7 Supported Crops)
        crop_info = SUPPORTED_CROPS_INFO.get(detected_crop, {})
        allowed_classes = crop_info.get("disease_classes", [])
        if not allowed_classes or not self.disease_model:
            return {
                "status": "unsupported_crop",
                "title": "Unsupported Crop",
                "message": f"Disease classification is not configured for {detected_crop}.",
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        img_resized = img_pil.convert("RGB").resize((224, 224))
        img_arr = np.expand_dims(np.array(img_resized, dtype=np.float32), 0)
        raw_disease_preds = self.disease_model.predict(img_arr, verbose=0)[0]

        # Extract probabilities strictly for the allowed classes of this validated crop
        allowed_indices = [self.disease_classes.index(cls_name) for cls_name in allowed_classes if cls_name in self.disease_classes]
        if not allowed_indices:
            return {
                "status": "unsupported_crop",
                "title": f"{crop_info.get('display_name', detected_crop)} Model Pending Training",
                "message": f"The pathology catalog for {crop_info.get('display_name', detected_crop)} is registered, but CNN weights must be fine-tuned with training leaf images before live inference can be enabled.",
                "confidence": None,
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }
        allowed_scores = [float(raw_disease_preds[idx]) for idx in allowed_indices]
        
        # Softmax re-normalization over the crop's allowed disease classes
        total_sub_score = sum(allowed_scores) + 1e-9
        norm_sub_scores = [s / total_sub_score for s in allowed_scores]

        best_sub_idx = int(np.argmax(norm_sub_scores))
        chosen_class = allowed_classes[best_sub_idx]
        chosen_sub_conf = norm_sub_scores[best_sub_idx]

        # If a soybean leaf is uploaded but disease confidence is ambiguous or doesn't match trained diseases
        if detected_crop == "Soybean" and (chosen_sub_conf < 0.40 or sum(allowed_scores) < 0.15):
            return {
                "status": "ambiguous_disease",
                "title": "Uncertain Soybean Condition",
                "message": "Soybean detected, but disease could not be reliably identified.",
                "crop": "Soybean",
                "confidence": round(float(chosen_sub_conf) * 100, 2),
                "supported_crops": [info["display_name"] for k, info in SUPPORTED_CROPS_INFO.items() if info["supports_disease"]]
            }

        # Overall confidence combining crop validation confidence and disease sub-confidence
        combined_conf = chosen_sub_conf * min(1.0, crop_prob)
        exact_conf = round(combined_conf * 100, 2)

        # Lookup disease advisory info
        rec = self.disease_info.get(chosen_class)
        if not rec:
            crop_display = crop_info.get("display_name", detected_crop)
            disease_display = chosen_class.split("___")[-1].replace("_", " ")
            rec = {
                "class_name": chosen_class,
                "crop_name": crop_display,
                "disease_name": disease_display,
                "description": f"Identified condition: {disease_display} on {crop_display}.",
                "symptoms": ["Visible foliar discoloration or leaf spotting."],
                "prevention": ["Practice crop rotation and avoid overhead watering."],
                "treatment_or_cure": ["Remove affected leaves and monitor plant vigor."],
                "chemical_information": "Consult local agricultural extension service for registered fungicides/bactericides.",
                "disclaimer": "Advisory information is for guidance only."
            }

        return {
            "status": "success",
            "crop": rec.get("crop_name", crop_info.get("display_name", detected_crop)),
            "disease": rec.get("disease_name", chosen_class.split("___")[-1].replace("_", " ")),
            "class_name": chosen_class,
            "raw_probability": float(chosen_sub_conf),
            "crop_probability": float(crop_prob),
            "confidence": exact_conf,
            "recommendation": rec
        }

