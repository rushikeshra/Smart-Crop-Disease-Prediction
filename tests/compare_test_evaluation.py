import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import numpy as np
from PIL import Image

from ml.crop_validator import CropSystemValidator, SUPPORTED_CROPS_INFO

def main():
    print("=" * 80)
    print("OOD REJECTION & IN-DISTRIBUTION VERIFICATION")
    print("=" * 80)
    sys.stdout.flush()

    validator = CropSystemValidator.get_instance()
    
    # -------------------------------------------------------------
    # 1. Load In-Distribution Test Set (519 images)
    # -------------------------------------------------------------
    test_dir = os.path.join("dataset", "processed", "test")
    class_to_crop = {}
    for cname, info in SUPPORTED_CROPS_INFO.items():
        for d in info["disease_classes"]:
            class_to_crop[d] = cname

    test_samples = []
    for d_cls in sorted(os.listdir(test_dir)):
        d_path = os.path.join(test_dir, d_cls)
        if not os.path.isdir(d_path):
            continue
        c_name = class_to_crop[d_cls]
        for fname in sorted(os.listdir(d_path)):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            p = os.path.join(d_path, fname)
            test_samples.append({
                "path": p,
                "disease_gt": d_cls,
                "crop_gt": c_name,
                "filename": fname
            })

    print(f"Loaded {len(test_samples)} in-distribution test samples from {test_dir}")
    sys.stdout.flush()

    # Pre-extract test features and predictions in batches
    print("Extracting features and predictions for in-distribution test set...")
    sys.stdout.flush()

    batch_size = 32
    for i in range(0, len(test_samples), batch_size):
        batch = test_samples[i:i + batch_size]
        imgs = []
        for s in batch:
            im = Image.open(s["path"]).convert("RGB")
            # Foliar and fruit checks
            is_foliar, foliar_reason = validator.check_foliar_integrity(im)
            is_fruit, fruit_reason = validator.check_fruit_content(im)
            s["is_foliar"] = is_foliar
            s["foliar_reason"] = foliar_reason
            s["is_fruit"] = is_fruit
            s["fruit_reason"] = fruit_reason
            
            # Array for models
            im_resized = im.resize((224, 224))
            imgs.append(np.array(im_resized, dtype=np.float32))

        batch_arr = np.array(imgs, dtype=np.float32)

        # Crop model predictions
        crop_preds = validator.crop_model.predict(batch_arr, verbose=0)
        # Crop feature embeddings
        crop_feats = validator.crop_feat_extractor.predict(batch_arr, verbose=0)
        # Disease model predictions
        disease_preds = validator.disease_model.predict(batch_arr, verbose=0)

        for j, s in enumerate(batch):
            s["crop_probs"] = crop_preds[j]
            top_c_idx = int(np.argmax(crop_preds[j]))
            s["top_crop"] = validator.crop_classes[top_c_idx]
            s["top_crop_prob"] = float(crop_preds[j][top_c_idx])

            feat = crop_feats[j]
            feat_norm = feat / (np.linalg.norm(feat) + 1e-7)
            s["feat_norm"] = feat_norm

            s["disease_probs"] = disease_preds[j]

    print("In-distribution test preprocessing complete.")
    sys.stdout.flush()

    # -------------------------------------------------------------
    # 2. Load Unseen OOD Set (59 images)
    # -------------------------------------------------------------
    ood_dir = os.path.join("scratch", "eval_dataset")
    ood_samples = []
    for cat in sorted(os.listdir(ood_dir)):
        c_path = os.path.join(ood_dir, cat)
        if not os.path.isdir(c_path):
            continue
        for fname in sorted(os.listdir(c_path)):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            p = os.path.join(c_path, fname)
            ood_samples.append({
                "path": p,
                "category": cat,
                "filename": fname
            })

    print(f"Loaded {len(ood_samples)} unseen OOD samples from {ood_dir}")
    sys.stdout.flush()

    print("Extracting features and predictions for OOD set...")
    for i in range(0, len(ood_samples), batch_size):
        batch = ood_samples[i:i + batch_size]
        imgs = []
        for s in batch:
            im = Image.open(s["path"]).convert("RGB")
            is_foliar, foliar_reason = validator.check_foliar_integrity(im)
            is_fruit, fruit_reason = validator.check_fruit_content(im)
            s["is_foliar"] = is_foliar
            s["foliar_reason"] = foliar_reason
            s["is_fruit"] = is_fruit
            s["fruit_reason"] = fruit_reason

            im_resized = im.resize((224, 224))
            imgs.append(np.array(im_resized, dtype=np.float32))

        batch_arr = np.array(imgs, dtype=np.float32)
        crop_preds = validator.crop_model.predict(batch_arr, verbose=0)
        crop_feats = validator.crop_feat_extractor.predict(batch_arr, verbose=0)
        disease_preds = validator.disease_model.predict(batch_arr, verbose=0)

        for j, s in enumerate(batch):
            s["crop_probs"] = crop_preds[j]
            top_c_idx = int(np.argmax(crop_preds[j]))
            s["top_crop"] = validator.crop_classes[top_c_idx]
            s["top_crop_prob"] = float(crop_preds[j][top_c_idx])

            feat = crop_feats[j]
            feat_norm = feat / (np.linalg.norm(feat) + 1e-7)
            s["feat_norm"] = feat_norm

            s["disease_probs"] = disease_preds[j]

    print("OOD preprocessing complete.\n")
    sys.stdout.flush()

    # -------------------------------------------------------------
    # Evaluation function for a given set of centroids / thresholds
    # -------------------------------------------------------------
    def evaluate_configuration(config_name, bp_threshold, corn_threshold):
        centroids_config = json.loads(json.dumps(validator.crop_centroids))
        centroids_config["Bell_Pepper"]["ood_threshold"] = bp_threshold
        centroids_config["Corn"]["ood_threshold"] = corn_threshold

        # --- In-distribution evaluation ---
        id_correct_crop = 0
        id_correct_disease = 0
        false_rejections = 0
        false_rejection_reasons = []

        for s in test_samples:
            if not s["is_foliar"]:
                false_rejections += 1
                false_rejection_reasons.append((s["filename"], s["crop_gt"], s["disease_gt"], "foliar_check", 0.0, 0.0))
                continue
            if s["is_fruit"]:
                false_rejections += 1
                false_rejection_reasons.append((s["filename"], s["crop_gt"], s["disease_gt"], "fruit_check", 0.0, 0.0))
                continue

            top_crop = s["top_crop"]
            top_prob = s["top_crop_prob"]
            if top_crop == s["crop_gt"]:
                id_correct_crop += 1

            centroid = np.array(centroids_config[top_crop]["centroid"], dtype=np.float32)
            cos_sim = float(np.dot(s["feat_norm"], centroid))
            tau = centroids_config[top_crop]["ood_threshold"]

            if cos_sim < tau or top_prob < 0.45:
                false_rejections += 1
                false_rejection_reasons.append((s["filename"], s["crop_gt"], s["disease_gt"], f"ood_gate (sim={cos_sim:.4f} < tau={tau:.4f})", cos_sim, tau))
                continue

            # Soybean rule
            if top_crop == "Soybean":
                soy_idx = validator.disease_classes.index("Soybean___healthy")
                if s["disease_probs"][soy_idx] < 0.70:
                    false_rejections += 1
                    false_rejection_reasons.append((s["filename"], s["crop_gt"], s["disease_gt"], "soybean_rule", cos_sim, tau))
                    continue

            # Crop-constrained disease classification
            allowed_classes = SUPPORTED_CROPS_INFO[top_crop]["disease_classes"]
            allowed_indices = [validator.disease_classes.index(c) for c in allowed_classes if c in validator.disease_classes]
            sub_probs = {validator.disease_classes[i]: float(s["disease_probs"][i]) for i in allowed_indices}
            chosen_disease = max(sub_probs, key=sub_probs.get)

            if chosen_disease == s["disease_gt"]:
                id_correct_disease += 1

        # --- OOD evaluation ---
        ood_correct_rejected = 0
        false_acceptances = 0
        false_acceptance_details = []

        for s in ood_samples:
            # Stage 1: Foliar check
            if not s["is_foliar"]:
                ood_correct_rejected += 1
                continue
            # Stage 2: Fruit check
            if s["is_fruit"]:
                ood_correct_rejected += 1
                continue

            top_crop = s["top_crop"]
            top_prob = s["top_crop_prob"]
            centroid = np.array(centroids_config[top_crop]["centroid"], dtype=np.float32)
            cos_sim = float(np.dot(s["feat_norm"], centroid))
            tau = centroids_config[top_crop]["ood_threshold"]

            # Stage 3: OOD gate
            if cos_sim < tau or top_prob < 0.45:
                ood_correct_rejected += 1
                continue

            # Stage 4: Soybean rule
            if top_crop == "Soybean":
                soy_idx = validator.disease_classes.index("Soybean___healthy")
                if s["disease_probs"][soy_idx] < 0.70:
                    ood_correct_rejected += 1
                    continue

            # If it reaches here, it was falsely accepted!
            false_acceptances += 1
            # Top disease prediction if it were diagnosed:
            allowed_classes = SUPPORTED_CROPS_INFO[top_crop]["disease_classes"]
            allowed_indices = [validator.disease_classes.index(c) for c in allowed_classes if c in validator.disease_classes]
            sub_probs = {validator.disease_classes[i]: float(s["disease_probs"][i]) for i in allowed_indices}
            chosen_disease = max(sub_probs, key=sub_probs.get)
            chosen_d_prob = sub_probs[chosen_disease]

            false_acceptance_details.append({
                "path": s["path"],
                "category": s["category"],
                "crop_pred": top_crop,
                "crop_prob": top_prob,
                "cosine_sim": cos_sim,
                "threshold": tau,
                "disease_pred": chosen_disease,
                "disease_prob": chosen_d_prob
            })

        crop_acc = id_correct_crop / len(test_samples) * 100.0
        disease_acc = id_correct_disease / len(test_samples) * 100.0
        ood_rejection_rate = ood_correct_rejected / len(ood_samples) * 100.0

        return {
            "name": config_name,
            "bp_threshold": bp_threshold,
            "corn_threshold": corn_threshold,
            "crop_accuracy": crop_acc,
            "disease_accuracy": disease_acc,
            "id_correct_crop": id_correct_crop,
            "id_correct_disease": id_correct_disease,
            "total_test": len(test_samples),
            "false_rejections": false_rejections,
            "false_rejection_reasons": false_rejection_reasons,
            "ood_rejection_rate": ood_rejection_rate,
            "ood_correct_rejected": ood_correct_rejected,
            "total_ood": len(ood_samples),
            "false_acceptances": false_acceptances,
            "false_acceptance_details": false_acceptance_details
        }

    # Evaluate Before vs After
    res_before = evaluate_configuration("BEFORE Calibration", 0.7800, 0.7500)
    res_after = evaluate_configuration("AFTER Calibration", 0.7850, 0.7600)

    for r in [res_before, res_after]:
        print("=" * 80)
        print(f"CONFIGURATION: {r['name']}")
        print(f"Thresholds: Bell Pepper = {r['bp_threshold']:.4f}, Corn = {r['corn_threshold']:.4f}")
        print("-" * 80)
        print(f"  Disease Accuracy:      {r['disease_accuracy']:.2f}% ({r['id_correct_disease']}/{r['total_test']})")
        print(f"  Crop Accuracy:         {r['crop_accuracy']:.2f}% ({r['id_correct_crop']}/{r['total_test']})")
        print(f"  OOD Rejection Rate:    {r['ood_rejection_rate']:.2f}% ({r['ood_correct_rejected']}/{r['total_ood']})")
        print(f"  False Acceptance Count:{r['false_acceptances']} / {r['total_ood']}")
        print(f"  False Rejection Count: {r['false_rejections']} / {r['total_test']} ({r['false_rejections']/r['total_test']*100:.2f}%)")
        print("-" * 80)
        if r['false_acceptances'] > 0:
            print("  FALSE ACCEPTANCES:")
            for fa in r['false_acceptance_details']:
                print(f"    - Path: {fa['path']}")
                print(f"      Category: {fa['category']}")
                print(f"      Predicted Crop: {fa['crop_pred']} (prob: {fa['crop_prob']:.6f})")
                print(f"      Cosine Sim: {fa['cosine_sim']:.4f} vs tau: {fa['threshold']:.4f}")
                print(f"      Predicted Disease: {fa['disease_pred']} (prob: {fa['disease_prob']:.6f})")
        else:
            print("  FALSE ACCEPTANCES: NONE (0 images accepted - 100.0% rejected)")

        if r['false_rejections'] > 0:
            print(f"  FALSE REJECTIONS ({r['false_rejections']} images):")
            for fr in r['false_rejection_reasons']:
                print(f"    - File: {fr[0]}, GT Crop: {fr[1]}, GT Disease: {fr[2]}, Reason: {fr[3]}")
        print()

    # Save summary to JSON for reporting
    output_path = os.path.join("tests", "calibration_comparison_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        # filter non-serializable
        clean_res = {
            "before": {k: v for k, v in res_before.items() if k != "feat_norm"},
            "after": {k: v for k, v in res_after.items() if k != "feat_norm"}
        }
        json.dump(clean_res, f, indent=2)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
