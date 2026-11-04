import os
import sys
import argparse
import hashlib
from collections import defaultdict
from PIL import Image

def get_file_md5(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def inspect_dataset(data_dir, output_report_path=None, filter_crops=None):
    print("=" * 75)
    print(f"INSPECTING DATASET AT: {data_dir}")
    print("=" * 75)

    if not os.path.exists(data_dir):
        print(f"[ERROR] Directory not found: {data_dir}")
        print("Please place your dataset inside dataset/raw or pass --data_dir <path>")
        return None

    entries = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    if not entries:
        print(f"[WARNING] No class subdirectories found directly in {data_dir}.")
        return None

    target_classes = []
    excluded_classes = []
    
    for d in sorted(entries):
        if filter_crops:
            if any(crop.lower() in d.lower() for crop in filter_crops):
                target_classes.append(d)
            else:
                excluded_classes.append(d)
        else:
            # Auto-detect all crop classes in dataset
            target_classes.append(d)

    print(f"\n[1] CLASS DISCOVERY & DETECTION:")
    print(f"    - Total classes detected ({len(target_classes)}):")
    for idx, tc in enumerate(target_classes, 1):
        print(f"      {idx:>2}. {tc}")
    
    if excluded_classes:
        print(f"    - Filtered out classes ({len(excluded_classes)}):")
        for ec in excluded_classes:
            print(f"      * {ec}")

    if not target_classes:
        print("\n[ERROR] No valid class folders found to inspect.")
        return None

    # Image Integrity & Audit
    class_counts = {}
    class_dimensions = defaultdict(set)
    corrupted_files = []
    unsupported_files = []
    empty_classes = []
    file_hashes = defaultdict(list)
    total_valid_images = 0

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

    print("\n[2] SCANNING IMAGE INTEGRITY & VALIDATION:")
    for cls_name in target_classes:
        cls_dir = os.path.join(data_dir, cls_name)
        files = os.listdir(cls_dir)
        
        valid_class_images = 0
        if not files:
            empty_classes.append(cls_name)
            class_counts[cls_name] = 0
            continue

        for fname in files:
            fpath = os.path.join(cls_dir, fname)
            if os.path.isdir(fpath):
                continue
            
            ext = os.path.splitext(fname)[1].lower()
            if ext not in valid_extensions:
                unsupported_files.append((cls_name, fname, ext))
                continue

            try:
                with Image.open(fpath) as img:
                    img.verify()
                
                with Image.open(fpath) as img:
                    class_dimensions[cls_name].add(img.size)
                
                md5 = get_file_md5(fpath)
                if md5:
                    file_hashes[md5].append((cls_name, fname))

                valid_class_images += 1
                total_valid_images += 1
            except Exception as e:
                corrupted_files.append((cls_name, fname, str(e)))

        class_counts[cls_name] = valid_class_images

    duplicate_groups = {h: flist for h, flist in file_hashes.items() if len(flist) > 1}

    print("\n" + "=" * 75)
    print("DATASET AUDIT REPORT")
    print("=" * 75)
    print(f"Total Detected Classes: {len(target_classes)}")
    print(f"Total Valid Images:     {total_valid_images}")
    print("\n[IMAGE COUNT PER CLASS]")
    for cls_name, count in class_counts.items():
        dims = list(class_dimensions[cls_name])[:2]
        dims_str = ", ".join([f"{w}x{h}" for w, h in dims]) if dims else "N/A"
        print(f"  - {cls_name:<46}: {count:>5} images (Sample size: {dims_str})")

    print("\n[INTEGRITY AUDIT FINDINGS]")
    print(f"  - Corrupted Images:       {len(corrupted_files)}")
    if corrupted_files:
        for c in corrupted_files[:5]:
            print(f"    ! Corrupted file: {c[0]}/{c[1]} - {c[2]}")
    
    print(f"  - Unsupported Extensions: {len(unsupported_files)}")
    print(f"  - Empty Folders:          {len(empty_classes)}")
    print(f"  - Duplicate Hashes Found: {len(duplicate_groups)} duplicate sets")

    if class_counts:
        counts = [c for c in class_counts.values() if c > 0]
        if counts:
            min_c = min(counts)
            max_c = max(counts)
            ratio = max_c / min_c if min_c > 0 else float("inf")
            print(f"\n[CLASS IMBALANCE]")
            print(f"  - Minimum Class Size: {min_c}")
            print(f"  - Maximum Class Size: {max_c}")
            print(f"  - Imbalance Ratio:    {ratio:.2f}:1")

    print("=" * 75)

    report_data = {
        "classes": target_classes,
        "class_counts": class_counts,
        "total_valid_images": total_valid_images,
        "corrupted_count": len(corrupted_files),
        "duplicates_count": len(duplicate_groups)
    }
    return report_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Crop Disease Dataset")
    parser.add_argument("--data_dir", type=str, default="dataset/raw", help="Path to raw dataset")
    parser.add_argument("--filter_crops", nargs="*", default=None, help="Optional crop names to filter")
    args = parser.parse_args()

    inspect_dataset(os.path.abspath(args.data_dir), filter_crops=args.filter_crops)
