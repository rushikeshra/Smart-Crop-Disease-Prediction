import os
import sys
import glob
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ml.crop_validator import CropSystemValidator, SUPPORTED_CROPS_INFO

def run_comprehensive_tests():
    validator = CropSystemValidator.get_instance()
    
    print("=" * 80)
    print("COMPREHENSIVE MULTI-IMAGE PIPELINE VERIFICATION")
    print("=" * 80)

    # Test cases to evaluate
    test_cases = []

    # 1. User uploaded soybean image
    user_uploaded_path = os.path.join(BASE_DIR, "static", "uploads", "leaf_c141119cad69.jpg")
    if os.path.exists(user_uploaded_path):
        test_cases.append({
            "name": "User Uploaded Soybean Leaf",
            "path": user_uploaded_path,
            "expected_category": "Soybean (Diseased / Foliar Pathogen)",
            "expected_status": "success",
            "must_not_contain": ["Bell Pepper", "Pepper__bell___Bacterial_spot"]
        })

    # 2. Soybean Unseen Test Set Images (1 from each class)
    soy_test_dir = os.path.join(BASE_DIR, "dataset", "processed", "test")
    for soy_cls in ["Soybean___healthy", "Soybean___Bacterial_blight", "Soybean___Frogeye_leaf_spot", "Soybean___Soybean_rust"]:
        cls_dir = os.path.join(soy_test_dir, soy_cls)
        if os.path.exists(cls_dir):
            imgs = glob.glob(os.path.join(cls_dir, "*.*"))
            if imgs:
                test_cases.append({
                    "name": f"Unseen {soy_cls}",
                    "path": imgs[0],
                    "expected_category": soy_cls.replace("___", " - "),
                    "expected_status": "success",
                    "expected_class": soy_cls
                })

    # 3. Supported Crops (Healthy & Diseased)
    sample_images = [
        ("Pepper__bell___Bacterial_spot", "Bell Pepper - Bacterial Spot"),
        ("Corn_(maize)___Common_rust_", "Corn - Common Rust"),
        ("Tomato___Early_blight", "Tomato - Early Blight"),
        ("Apple___healthy", "Apple - Healthy Foliage"),
        ("Cotton___Bacterial_blight", "Cotton - Bacterial Blight"),
        ("Cotton___healthy", "Cotton - Healthy Foliage"),
        ("Green_Gram___Cercospora_leaf_spot", "Green Gram - Cercospora Leaf Spot"),
        ("Green_Gram___healthy", "Green Gram - Healthy Foliage"),
        ("Pigeon_Pea___Sterility_mosaic", "Pigeon Pea - Sterility Mosaic"),
        ("Pigeon_Pea___healthy", "Pigeon Pea - Healthy Foliage")
    ]
    for cls_name, display in sample_images:
        cls_dir = os.path.join(soy_test_dir, cls_name)
        if os.path.exists(cls_dir):
            imgs = glob.glob(os.path.join(cls_dir, "*.*"))
            if imgs:
                test_cases.append({
                    "name": f"Supported: {display}",
                    "path": imgs[0],
                    "expected_category": display,
                    "expected_status": "success",
                    "expected_class": cls_name
                })

    # 4. OOD / Unsupported Crop Samples (Rice, Wheat)
    eval_dir = os.path.join(BASE_DIR, "scratch", "eval_dataset")
    for ood_type in ["rice", "wheat"]:
        ood_path = os.path.join(eval_dir, ood_type)
        if os.path.exists(ood_path):
            imgs = glob.glob(os.path.join(ood_path, "*.*"))
            if imgs:
                test_cases.append({
                    "name": f"Unsupported Crop ({ood_type.capitalize()})",
                    "path": imgs[0],
                    "expected_category": "Unsupported Crop (Rejected)",
                    "expected_status": "unsupported_crop"
                })

    # 5. OOD / Non-Leaf & Fruit
    for ood_type in ["fruit", "non_leaf"]:
        ood_path = os.path.join(eval_dir, ood_type)
        if os.path.exists(ood_path):
            imgs = glob.glob(os.path.join(ood_path, "*.*"))
            if imgs:
                test_cases.append({
                    "name": f"Non-Foliar ({ood_type.capitalize()})",
                    "path": imgs[0],
                    "expected_category": "Invalid / Non-leaf (Rejected)",
                    "expected_status": ["invalid_image", "unsupported_crop"]
                })

    # Run evaluations
    results = []
    print(f"\n{'Test Case':<32} | {'Expected':<26} | {'Actual Diagnosis':<30} | {'Conf':<7} | {'Result':<6}")
    print("-" * 115)

    for tc in test_cases:
        diag = validator.diagnose_leaf(tc["path"])
        status = diag.get("status")
        conf = diag.get("confidence")
        conf_str = f"{conf:.1f}%" if conf is not None else "N/A"
        
        if status == "success":
            actual_str = f"{diag.get('crop')} - {diag.get('disease')}"
        elif status == "unsupported_crop":
            actual_str = f"Unsupported Crop ({diag.get('detected_candidate', 'Unknown')})"
        elif status == "invalid_image":
            actual_str = f"Invalid/Non-leaf: {diag.get('title')}"
        elif status == "ambiguous_disease":
            actual_str = "Ambiguous Soybean Condition"
        else:
            actual_str = f"Status: {status}"

        # Evaluate Pass/Fail
        passed = False
        exp_status = tc["expected_status"]
        if isinstance(exp_status, list):
            passed = status in exp_status
        else:
            passed = (status == exp_status)

        if "expected_class" in tc and status == "success":
            if diag.get("class_name") != tc["expected_class"]:
                passed = False

        if "must_not_contain" in tc and status == "success":
            for bad_str in tc["must_not_contain"]:
                if bad_str in str(diag):
                    passed = False

        pass_str = "PASS" if passed else "FAIL"
        print(f"{tc['name'][:32]:<32} | {tc['expected_category'][:26]:<26} | {actual_str[:30]:<30} | {conf_str:<7} | {pass_str:<6}")

        results.append({
            "name": tc["name"],
            "expected": tc["expected_category"],
            "actual": actual_str,
            "status": status,
            "confidence": conf,
            "passed": passed,
            "details": diag
        })

    print("-" * 115)
    total_passed = sum(1 for r in results if r["passed"])
    print(f"Total Tests: {len(results)} | Passed: {total_passed} | Failed: {len(results) - total_passed}")
    print("=" * 115)

    return results

if __name__ == "__main__":
    run_comprehensive_tests()
