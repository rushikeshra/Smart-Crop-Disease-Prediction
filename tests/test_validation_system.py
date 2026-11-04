import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from ml.crop_validator import CropSystemValidator

def run_tests():
    scratch_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", "test_images")
    os.makedirs(scratch_dir, exist_ok=True)

    # 1. Known supported healthy leaf
    t1 = "sample_crop_images/tomato_sample_2_healthy.jpg"

    # 2. Known supported diseased leaf
    t2 = "sample_crop_images/pepper_sample_1_bacterial_spot.jpg"

    # 3a. Healthy Soybean leaf
    t3a = "sample_crop_images/soybean_sample_1_healthy.jpg"

    # 3b. User's uploaded diseased soybean leaf
    t3b = "static/uploads/leaf_c141119cad69.jpg"

    # 4. Another unsupported crop (synthetic slender grass blade with pale background)
    unsupported_crop = Image.new("RGB", (224, 224), (210, 210, 195))
    for y in range(224):
        for x in range(104, 120):
            unsupported_crop.putpixel((x, y), (130, 160, 50))
    t4 = os.path.join(scratch_dir, "unsupported_rice_leaf.jpg")
    unsupported_crop.save(t4)

    # 5. Random non-leaf image (indoor wooden furniture / office desk)
    non_leaf = Image.new("RGB", (224, 224), (160, 110, 80))
    for y in range(0, 224, 20):
        for x in range(224):
            non_leaf.putpixel((x, y), (100, 70, 50))
    t5 = os.path.join(scratch_dir, "non_leaf_desk.jpg")
    non_leaf.save(t5)

    # 6. Fruit image (isolated round red apple/tomato fruit)
    fruit = Image.new("RGB", (224, 224), (230, 230, 230))
    for y in range(224):
        for x in range(224):
            if (x-112)**2 + (y-112)**2 < 75**2:
                fruit.putpixel((x, y), (210, 25, 25))
    t6 = os.path.join(scratch_dir, "fruit_apple.jpg")
    fruit.save(t6)

    # 7. Poor-quality / unclear image (blank / near-uniform gray)
    blank = Image.new("RGB", (224, 224), (128, 128, 128))
    t7 = os.path.join(scratch_dir, "blank_unclear.jpg")
    blank.save(t7)

    tests = [
        ("TEST 1: Supported Healthy Leaf (Tomato)", t1),
        ("TEST 2: Supported Diseased Leaf (Pepper Bacterial Spot)", t2),
        ("TEST 3a: Supported Healthy Leaf (Soybean Healthy)", t3a),
        ("TEST 3b: Diseased Soybean Leaf (User Uploaded Image)", t3b),
        ("TEST 4: Unsupported Crop Leaf (Rice/Wheat)", t4),
        ("TEST 5: Random Non-Leaf Image (Furniture/Desk)", t5),
        ("TEST 6: Fruit Image (Apple/Tomato Fruit)", t6),
        ("TEST 7: Poor-Quality / Blank Image", t7)
    ]

    v = CropSystemValidator.get_instance()
    print("=" * 80)
    print("SMARTCROP AI - VALIDATION AND INFERENCE TEST SUITE")
    print("=" * 80)

    for name, path in tests:
        res = v.diagnose_leaf(path)
        status = res.get("status")
        crop = res.get("crop") or res.get("detected_candidate")
        disease = res.get("disease")
        conf = res.get("confidence")
        msg = res.get("message")
        title = res.get("title")

        print(f"\n>>> {name}:")
        print(f"    Path:       {path}")
        print(f"    Status:     {status}")
        print(f"    Title:      {title}")
        print(f"    Crop:       {crop}")
        print(f"    Condition:  {disease}")
        print(f"    Confidence: {conf}")
        print(f"    Message:    {msg}")

if __name__ == "__main__":
    run_tests()
