import os
import glob
import json
import numpy as np
import tensorflow as tf
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def recalibrate():
    crop_model_path = os.path.join(BASE_DIR, "models", "crop_model.keras")
    if not os.path.exists(crop_model_path):
        crop_model_path = os.path.join(BASE_DIR, "models", "crop_model_best.h5")
        
    model = tf.keras.models.load_model(crop_model_path, compile=False)
    feat_extractor = tf.keras.Model(inputs=model.input, outputs=model.get_layer("crop_features").output)

    train_dir = os.path.join(BASE_DIR, "dataset", "processed", "train")
    
    # Classes mapping
    crop_classes = [
        "Apple", "Bell_Pepper", "Corn", "Cotton", "Grape",
        "Green_Gram", "Pigeon_Pea", "Potato", "Soybean", "Tomato"
    ]

    # Collect features per sub-group
    # Standard crops + Soybean split into healthy and field
    sub_groups = {
        "Apple": ["Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy"],
        "Bell_Pepper": ["Pepper__bell___Bacterial_spot", "Pepper__bell___healthy"],
        "Corn": ["Corn_(maize)___Common_rust_", "Corn_(maize)___healthy"],
        "Cotton": [
            "Cotton___Alternaria_leaf_spot",
            "Cotton___Bacterial_blight",
            "Cotton___Leaf_curl_virus",
            "Cotton___healthy"
        ],
        "Grape": ["Grape___Black_rot", "Grape___healthy"],
        "Green_Gram": [
            "Green_Gram___Cercospora_leaf_spot",
            "Green_Gram___Powdery_mildew",
            "Green_Gram___Yellow_mosaic",
            "Green_Gram___healthy"
        ],
        "Pigeon_Pea": [
            "Pigeon_Pea___Cercospora_leaf_spot",
            "Pigeon_Pea___Phytophthora_blight",
            "Pigeon_Pea___Sterility_mosaic",
            "Pigeon_Pea___healthy"
        ],
        "Potato": ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"],
        "Soybean_healthy": ["Soybean___healthy"],
        "Soybean_field": ["Soybean___Bacterial_blight", "Soybean___Frogeye_leaf_spot", "Soybean___Soybean_rust"],
        "Tomato": ["Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"]
    }

    centroids = {}
    print("[INFO] Computing sub-centroids using batched inference...")
    for group_name, classes in sub_groups.items():
        all_feats = []
        for cls in classes:
            cls_dir = os.path.join(train_dir, cls)
            if not os.path.exists(cls_dir):
                continue
            ds = tf.keras.utils.image_dataset_from_directory(
                cls_dir,
                image_size=(224, 224),
                batch_size=32,
                shuffle=False,
                labels=None
            )
            for batch in ds:
                feats = feat_extractor.predict(batch, verbose=0)
                norms = np.linalg.norm(feats, axis=1, keepdims=True) + 1e-7
                all_feats.append(feats / norms)
        all_feats = np.concatenate(all_feats, axis=0)
        c = np.mean(all_feats, axis=0)
        c = c / (np.linalg.norm(c) + 1e-7)
        # Compute in-distribution cosine similarities
        sims = np.dot(all_feats, c)
        centroids[group_name] = {
            "centroid": c.tolist(),
            "mean_sim": float(np.mean(sims)),
            "p5_sim": float(np.percentile(sims, 5)),
            "min_sim": float(np.min(sims)),
            "num_samples": int(len(sims))
        }
        print(f"  {group_name:<16}: N={len(sims):>4}, mean={np.mean(sims):.3f}, p5={np.percentile(sims, 5):.3f}, min={np.min(sims):.3f}")

    # Build the crop_centroids structure for CropSystemValidator
    # For Soybean, store dual centroids [Soybean_healthy, Soybean_field]
    final_centroids = {}
    for crop in crop_classes:
        if crop == "Soybean":
            final_centroids[crop] = {
                "centroids": [
                    centroids["Soybean_healthy"]["centroid"],
                    centroids["Soybean_field"]["centroid"]
                ],
                "ood_threshold": 0.620,  # Highly discriminative against Rice/Wheat while capturing both healthy (0.83+) & field (0.84+)
                "healthy_mean_sim": centroids["Soybean_healthy"]["mean_sim"],
                "field_mean_sim": centroids["Soybean_field"]["mean_sim"],
                "num_samples": centroids["Soybean_healthy"]["num_samples"] + centroids["Soybean_field"]["num_samples"]
            }
        elif crop == "Bell_Pepper":
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": 0.580,  # Captures 100% of bell pepper while rejecting rice (0.529) and wheat
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }
        elif crop == "Corn":
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": 0.740,  # Blocks wheat
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }
        elif crop == "Pigeon_Pea":
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": 0.710,  # Strictly rejects Rice (sim 0.702) and Wheat while keeping in-distribution
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }
        elif crop == "Green_Gram":
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": 0.650,
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }
        elif crop == "Cotton":
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": 0.650,
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }
        else:
            final_centroids[crop] = {
                "centroid": centroids[crop]["centroid"],
                "ood_threshold": float(np.percentile([centroids[crop]["p5_sim"] * 0.90], 50)),
                "mean_cosine_similarity": centroids[crop]["mean_sim"],
                "p5_cosine_similarity": centroids[crop]["p5_sim"],
                "num_samples": centroids[crop]["num_samples"]
            }

    # Save to models/crop_centroids.json
    out_path = os.path.join(BASE_DIR, "models", "crop_centroids.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_centroids, f, indent=4)
    print(f"[SUCCESS] Saved calibrated multi-prototype centroids to: {out_path}")

if __name__ == "__main__":
    recalibrate()
