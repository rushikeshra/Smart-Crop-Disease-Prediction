import os
import shutil
import zipfile

SOURCE_DIR = r"C:\Users\ASUS\OneDrive\Desktop\BCA_Project"
TARGET_DIR = r"C:\Users\ASUS\OneDrive\Desktop\SmartCrop_Project"
ZIP_PATH = r"C:\Users\ASUS\OneDrive\Desktop\SmartCrop_Project.zip"

def export_smartcrop_project():
    print(f"[INFO] Exporting project from: {SOURCE_DIR}")
    print(f"[INFO] Target Desktop folder:  {TARGET_DIR}")
    print(f"[INFO] Target Desktop ZIP:     {ZIP_PATH}")

    # 1. Clean or create target directory
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Existing {TARGET_DIR} found. Cleaning up...")
        try:
            shutil.rmtree(TARGET_DIR, ignore_errors=True)
        except Exception as e:
            print(f"[WARNING] Could not remove {TARGET_DIR}: {e}")
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 2. Folders to copy
    folders = [
        "database",
        "dataset",
        "docs",
        "ml",
        "models",
        "sample_crop_images",
        "static",
        "templates",
        "tests",
        "training",
        "translations"
    ]

    for folder in folders:
        src = os.path.join(SOURCE_DIR, folder)
        dst = os.path.join(TARGET_DIR, folder)
        if os.path.exists(src):
            print(f"  -> Copying {folder}...")
            shutil.copytree(
                src, dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git*", "*.tmp", "*.log")
            )

    # Copy scratch/eval_dataset if present
    src_eval = os.path.join(SOURCE_DIR, "scratch", "eval_dataset")
    dst_eval = os.path.join(TARGET_DIR, "scratch", "eval_dataset")
    if os.path.exists(src_eval):
        print("  -> Copying scratch/eval_dataset...")
        shutil.copytree(
            src_eval, dst_eval,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )

    # 3. Root files to copy
    files = [
        ".env",
        ".env.example",
        ".gitignore",
        "AGENTS.md",
        "app.py",
        "config.py",
        "predict_sample.py",
        "prepare_samples.py",
        "README.md",
        "requirements.txt",
        "run_project.bat",
        "run_tests.bat",
        "SAMPLE_LEAF_IMAGES_GUIDE.md",
        "test_app.py",
        "VIVA_QUESTIONS_GUIDE.md"
    ]

    for f in files:
        src = os.path.join(SOURCE_DIR, f)
        dst = os.path.join(TARGET_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  -> Copied file: {f}")

    # 4. Create launcher scripts in TARGET_DIR
    run_bat_content = """@echo off
title Smart Crop AI - SmartCrop_Project
echo ======================================================================
echo           SMART CROP AI: MULTILINGUAL DISEASE PREDICTION SYSTEM
echo ======================================================================
echo.
cd /d "%~dp0"
python app.py
pause
"""
    with open(os.path.join(TARGET_DIR, "run_project.bat"), "w", encoding="utf-8") as f:
        f.write(run_bat_content)

    test_bat_content = """@echo off
title Run Verification Tests - SmartCrop_Project
echo ======================================================================
echo                  RUNNING TEST SUITES
echo ======================================================================
cd /d "%~dp0"
echo [1/3] Running Core Unit Tests:
python -m unittest test_app.py
echo.
echo [2/3] Running Multilingual System Tests (English, Hindi, Marathi):
python -m unittest tests/test_multilingual_system.py
echo.
echo [3/3] Running Comprehensive Multi-Image Pipeline Verification:
python training/comprehensive_verification.py
pause
"""
    with open(os.path.join(TARGET_DIR, "run_tests.bat"), "w", encoding="utf-8") as f:
        f.write(test_bat_content)

    print(f"\n[SUCCESS] Successfully exported to folder: {TARGET_DIR}")

    # 5. Create ZIP Archive
    print(f"\n[INFO] Creating ZIP archive: {ZIP_PATH} ...")
    tmp_zip = ZIP_PATH + ".tmp"
    if os.path.exists(tmp_zip):
        os.remove(tmp_zip)

    with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, filenames in os.walk(TARGET_DIR):
            for file in filenames:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, TARGET_DIR)
                arcname = os.path.join("SmartCrop_Project", rel_path)
                zipf.write(file_path, arcname)

    if os.path.exists(ZIP_PATH):
        try:
            os.remove(ZIP_PATH)
        except Exception:
            pass

    if os.path.exists(ZIP_PATH):
        try:
            os.replace(tmp_zip, ZIP_PATH)
        except Exception:
            pass
    else:
        os.rename(tmp_zip, ZIP_PATH)

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[SUCCESS] Successfully created ZIP archive: {ZIP_PATH} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    export_smartcrop_project()
