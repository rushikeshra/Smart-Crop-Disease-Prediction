import os
import sys
import shutil
import argparse
import random
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

def normalize_class_name(name):
    """Normalize raw directory name to match disease_info.json format."""
    return name.replace(",_", "__").replace(" ", "_")

def prepare_dataset(raw_dir, output_dir, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42, filter_crops=None, max_samples_per_class=None, exact_classes=None):
    random.seed(seed)
    
    print("=" * 75)
    print("PREPARING DATASET SPLIT (STRATIFIED & LEAKAGE-FREE)")
    print("=" * 75)
    print(f"Source: {raw_dir}")
    print(f"Output: {output_dir}")
    print(f"Ratios: Train: {train_ratio*100:.0f}%, Val: {val_ratio*100:.0f}%, Test: {test_ratio*100:.0f}%")
    print(f"Seed:   {seed}")
    if max_samples_per_class:
        print(f"Cap:    {max_samples_per_class} samples/class")

    if not os.path.exists(raw_dir):
        print(f"[ERROR] Source dataset folder does not exist: {raw_dir}")
        return False

    all_subdirs = sorted([d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))])
    
    if exact_classes:
        raw_classes = [d for d in all_subdirs if d in exact_classes or normalize_class_name(d) in exact_classes]
    elif filter_crops:
        raw_classes = [d for d in all_subdirs if any(c.lower() in d.lower() for c in filter_crops)]
    else:
        raw_classes = all_subdirs
    
    if not raw_classes:
        print(f"[ERROR] No valid class folders found in {raw_dir}")
        return False

    # Clean output directory so previous split classes do not linger
    shutil.rmtree(output_dir, ignore_errors=True)

    splits = ["train", "val", "test"]
    target_classes = [normalize_class_name(c) for c in raw_classes]
    for s in splits:
        for t_cls in target_classes:
            os.makedirs(os.path.join(output_dir, s, t_cls), exist_ok=True)

    split_counts = {s: defaultdict(int) for s in splits}
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    all_seen_hashes = {}

    for cls in raw_classes:
        t_cls = normalize_class_name(cls)
        cls_raw_path = os.path.join(raw_dir, cls)
        all_files = sorted(os.listdir(cls_raw_path))
        
        valid_files = []
        for fname in all_files:
            fpath = os.path.join(cls_raw_path, fname)
            if not os.path.isfile(fpath):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in valid_extensions:
                continue
            
            try:
                with Image.open(fpath) as img:
                    img.verify()
                
                h = get_file_md5(fpath)
                if h:
                    if h in all_seen_hashes:
                        continue
                    all_seen_hashes[h] = fpath

                valid_files.append(fname)
            except Exception:
                continue

        random.shuffle(valid_files)
        if max_samples_per_class and len(valid_files) > max_samples_per_class:
            valid_files = valid_files[:max_samples_per_class]

        total_cls = len(valid_files)

        n_train = int(total_cls * train_ratio)
        n_val = int(total_cls * val_ratio)
        n_test = total_cls - n_train - n_val

        if total_cls >= 3:
            if n_train < 1: n_train = 1
            if n_val < 1: n_val = 1
            if n_test < 1: n_test = 1
            if n_train + n_val + n_test > total_cls:
                n_train = total_cls - n_val - n_test

        train_files = valid_files[:n_train]
        val_files = valid_files[n_train:n_train + n_val]
        test_files = valid_files[n_train + n_val:]

        for fname in train_files:
            shutil.copy2(os.path.join(cls_raw_path, fname), os.path.join(output_dir, "train", t_cls, fname))
            split_counts["train"][t_cls] += 1

        for fname in val_files:
            shutil.copy2(os.path.join(cls_raw_path, fname), os.path.join(output_dir, "val", t_cls, fname))
            split_counts["val"][t_cls] += 1

        for fname in test_files:
            shutil.copy2(os.path.join(cls_raw_path, fname), os.path.join(output_dir, "test", t_cls, fname))
            split_counts["test"][t_cls] += 1

    print("\n" + "=" * 75)
    print("STRATIFIED DATASET SPLIT SUMMARY")
    print("=" * 75)
    header = f"{'Class Name':<46} | {'Train':>7} | {'Val':>7} | {'Test':>7} | {'Total':>7}"
    print(header)
    print("-" * len(header))

    total_train = sum(split_counts["train"].values())
    total_val = sum(split_counts["val"].values())
    total_test = sum(split_counts["test"].values())

    for t_cls in target_classes:
        tr = split_counts["train"][t_cls]
        va = split_counts["val"][t_cls]
        te = split_counts["test"][t_cls]
        tot = tr + va + te
        print(f"{t_cls:<46} | {tr:>7} | {va:>7} | {te:>7} | {tot:>7}")

    print("-" * len(header))
    print(f"{'TOTAL SAMPLES':<46} | {total_train:>7} | {total_val:>7} | {total_test:>7} | {total_train+total_val+total_test:>7}")
    print("=" * 75)
    print("[SUCCESS] Dataset stratified split completed without data leakage.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split crop disease dataset into train/val/test")
    parser.add_argument("--raw_dir", type=str, default="dataset/raw", help="Path to raw dataset")
    parser.add_argument("--output_dir", type=str, default="dataset/processed", help="Path to output split dataset")
    parser.add_argument("--train_ratio", type=float, default=0.70, help="Train ratio (default: 0.70)")
    parser.add_argument("--val_ratio", type=float, default=0.15, help="Validation ratio (default: 0.15)")
    parser.add_argument("--test_ratio", type=float, default=0.15, help="Test ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--filter_crops", nargs="*", default=None, help="Optional crop names to filter")
    parser.add_argument("--exact_classes", nargs="*", default=None, help="Explicit class names to include")
    parser.add_argument("--max_samples_per_class", type=int, default=None, help="Maximum samples per class (for faster training)")
    args = parser.parse_args()

    prepare_dataset(
        os.path.abspath(args.raw_dir),
        os.path.abspath(args.output_dir),
        args.train_ratio,
        args.val_ratio,
        args.test_ratio,
        args.seed,
        filter_crops=args.filter_crops,
        max_samples_per_class=args.max_samples_per_class,
        exact_classes=args.exact_classes
    )
