import os
import sys
import json
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from ml.crop_validator import CropSystemValidator, SUPPORTED_CROPS_INFO

def run_verification():
    print("=" * 85)
    print("SMARTCROP AI - SYSTEM VERIFICATION AND BENCHMARK REPORT")
    print("=" * 85)

    # 1. Dataset Image Counts Per Class
    print("\n--- 1. DATASET IMAGE COUNTS PER CLASS ---")
    splits = ["train", "val", "test"]
    train_dir = os.path.join("dataset", "processed", "train")
    classes = sorted(os.listdir(train_dir))
    counts = {c: {} for c in classes}

    total_train = total_val = total_test = 0
    header = f"{'Class Name':<35} | {'Train':<6} | {'Val':<6} | {'Test':<6} | {'Total':<6}"
    print(header)
    print("-" * len(header))
    
    for c in classes:
        for s in splits:
            p = os.path.join("dataset", "processed", s, c)
            counts[c][s] = len(os.listdir(p)) if os.path.exists(p) else 0
        tr = counts[c]["train"]
        va = counts[c]["val"]
        te = counts[c]["test"]
        tot = tr + va + te
        total_train += tr
        total_val += va
        total_test += te
        print(f"{c:<35} | {tr:<6} | {va:<6} | {te:<6} | {tot:<6}")
    
    print("-" * len(header))
    print(f"{'TOTAL':<35} | {total_train:<6} | {total_val:<6} | {total_test:<6} | {total_train+total_val+total_test:<6}")

    # 2. Evaluation Metrics: Crop Classifier
    print("\n--- 2. CROP CLASSIFIER EVALUATION METRICS (INDEPENDENT TEST SET) ---")
    crop_metrics_path = os.path.join("models", "crop_evaluation_metrics.json")
    if os.path.exists(crop_metrics_path):
        with open(crop_metrics_path, "r", encoding="utf-8") as f:
            crop_metrics = json.load(f)
        print(f"Crop Classifier Test Accuracy: {crop_metrics.get('test_accuracy', 0.0) * 100:.2f}%\n")
        report = crop_metrics.get("classification_report", {})
        cr_header = f"{'Crop Class':<15} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}"
        print(cr_header)
        print("-" * len(cr_header))
        for crop_name in crop_metrics.get("crop_classes", []):
            if crop_name in report:
                p = report[crop_name]["precision"]
                r = report[crop_name]["recall"]
                f1 = report[crop_name]["f1-score"]
                sup = int(report[crop_name]["support"])
                print(f"{crop_name:<15} | {p:<10.4f} | {r:<10.4f} | {f1:<10.4f} | {sup:<8}")
        print("-" * len(cr_header))
        macro = report.get("macro avg", {})
        weighted = report.get("weighted avg", {})
        print(f"{'Macro Avg':<15} | {macro.get('precision', 0):<10.4f} | {macro.get('recall', 0):<10.4f} | {macro.get('f1-score', 0):<10.4f} | {int(macro.get('support', 0)):<8}")
        print(f"{'Weighted Avg':<15} | {weighted.get('precision', 0):<10.4f} | {weighted.get('recall', 0):<10.4f} | {weighted.get('f1-score', 0):<10.4f} | {int(weighted.get('support', 0)):<8}")

        print("\nCrop Classifier Confusion Matrix:")
        cm = np.array(crop_metrics.get("confusion_matrix", []))
        c_names = crop_metrics.get("crop_classes", [])
        col_hdr = "True \\ Pred".ljust(15) + " | " + " | ".join([f"{c[:6]:>6}" for c in c_names])
        print(col_hdr)
        print("-" * len(col_hdr))
        for idx, row in enumerate(cm):
            row_str = f"{c_names[idx]:<15} | " + " | ".join([f"{val:>6}" for val in row])
            print(row_str)

    # 3. Evaluation Metrics: Disease Model
    print("\n--- 3. DISEASE MODEL EVALUATION METRICS (INDEPENDENT TEST SET) ---")
    disease_metrics_path = os.path.join("models", "evaluation_metrics.json")
    if os.path.exists(disease_metrics_path):
        with open(disease_metrics_path, "r", encoding="utf-8") as f:
            dis_metrics = json.load(f)
        print(f"Disease Model Test Accuracy: {dis_metrics.get('test_accuracy', 0.0) * 100:.2f}%\n")
        d_report = dis_metrics.get("classification_report", {})
        dr_header = f"{'Disease Class':<35} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}"
        print(dr_header)
        print("-" * len(dr_header))
        for cls_name in classes:
            if cls_name in d_report:
                p = d_report[cls_name]["precision"]
                r = d_report[cls_name]["recall"]
                f1 = d_report[cls_name]["f1-score"]
                sup = int(d_report[cls_name]["support"])
                print(f"{cls_name:<35} | {p:<10.4f} | {r:<10.4f} | {f1:<10.4f} | {sup:<8}")
        print("-" * len(dr_header))

    # 4. Centroid Thresholds & OOD Settings
    print("\n--- 4. CALIBRATED CROP CENTROIDS & REJECTION THRESHOLDS ---")
    centroids_path = os.path.join("models", "crop_centroids.json")
    if os.path.exists(centroids_path):
        with open(centroids_path, "r", encoding="utf-8") as f:
            c_data = json.load(f)
        th_header = f"{'Crop Name':<15} | {'Train Mean Sim':<15} | {'5th Pctile':<12} | {'OOD Threshold':<14} | {'N Samples':<10}"
        print(th_header)
        print("-" * len(th_header))
        for crop, info in c_data.items():
            ms = info.get("mean_cosine_similarity", 0)
            p5 = info.get("p5_cosine_similarity", 0)
            th = info.get("ood_threshold", 0)
            ns = info.get("num_samples", 0)
            print(f"{crop:<15} | {ms:<15.4f} | {p5:<12.4f} | {th:<14.4f} | {ns:<10}")

    # 5. Live Test Image Predictions
    print("\n--- 5. LIVE TEST IMAGE PREDICTIONS & EVALUATION ---")
    validator = CropSystemValidator.get_instance()

    test_cases = [
        {
            "category": "Supported Healthy Leaf",
            "path": "sample_crop_images/tomato_sample_2_healthy.jpg",
            "expected_crop": "Tomato (Solanum lycopersicum)",
            "expected_condition": "Healthy Foliage",
            "expected_status": "success"
        },
        {
            "category": "Supported Diseased Leaf",
            "path": "sample_crop_images/pepper_sample_1_bacterial_spot.jpg",
            "expected_crop": "Bell Pepper (Capsicum)",
            "expected_condition": "Bacterial Spot (Xanthomonas campestris pv. vesicatoria)",
            "expected_status": "success"
        },
        {
            "category": "Soybean (Healthy Leaf)",
            "path": "sample_crop_images/soybean_sample_1_healthy.jpg",
            "expected_crop": "Soybean",
            "expected_condition": "Healthy Foliage",
            "expected_status": "success"
        },
        {
            "category": "Soybean (Diseased Leaf - User Photo)",
            "path": "static/uploads/leaf_c141119cad69.jpg",
            "expected_crop": "Unsupported Crop",
            "expected_condition": "Prediction unavailable — unsupported crop",
            "expected_status": "unsupported_crop"
        },
        {
            "category": "Another Unsupported Crop (Rice/Wheat Blade)",
            "path": "scratch/test_images/green_rice_blade.jpg",
            "expected_crop": "Unsupported Crop",
            "expected_condition": "Prediction unavailable — unsupported crop",
            "expected_status": "unsupported_crop"
        },
        {
            "category": "Random / Non-Leaf Image (Furniture Desk)",
            "path": "scratch/test_images/non_leaf_desk.jpg",
            "expected_crop": "Invalid / Non-Leaf Image",
            "expected_condition": "Prediction unavailable — invalid or non-leaf image",
            "expected_status": "invalid_image"
        },
        {
            "category": "Fruit Image (Apple/Tomato Fruit)",
            "path": "scratch/test_images/fruit_apple.jpg",
            "expected_crop": "Invalid / Non-Leaf Image",
            "expected_condition": "Prediction unavailable — invalid or non-leaf image",
            "expected_status": "invalid_image"
        }
    ]

    res_header = f"{'Test Image Category':<38} | {'Expected Result':<35} | {'Actual Result':<35} | {'Confidence':<12} | {'PASS/FAIL'}"
    print(res_header)
    print("-" * len(res_header))

    all_passed = True
    for tc in test_cases:
        p = tc["path"]
        res = validator.diagnose_leaf(p)
        status = res.get("status")
        
        if status == "success":
            actual_res = f"{res.get('crop')} - {res.get('disease')}"
            expected_res = f"{tc['expected_crop']} - {tc['expected_condition']}"
            conf_str = f"{res.get('confidence'):.1f}%"
            passed = (status == tc["expected_status"]) and (res.get("disease") == tc["expected_condition"])
        elif status == "unsupported_crop":
            actual_res = "Unsupported Crop (Rejected)"
            expected_res = f"{tc['expected_crop']} (Rejected)"
            conf_str = "None"
            passed = (status == tc["expected_status"])
        elif status == "invalid_image":
            actual_res = "Invalid Image (Rejected)"
            expected_res = f"{tc['expected_crop']} (Rejected)"
            conf_str = "None"
            passed = (status == tc["expected_status"])
        else:
            actual_res = f"Unknown ({status})"
            expected_res = tc["expected_status"]
            conf_str = "None"
            passed = False

        if not passed:
            all_passed = False

        status_tag = "PASS" if passed else "FAIL"
        print(f"{tc['category']:<38} | {expected_res:<35} | {actual_res:<35} | {conf_str:<12} | {status_tag}")

    print("-" * len(res_header))
    print(f"Overall Verification Suite: {'ALL TESTS PASSED [PASS]' if all_passed else 'SOME TESTS FAILED [FAIL]'}")

if __name__ == "__main__":
    run_verification()
