import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = BASE_DIR
TARGET_DIR = os.path.join(os.path.dirname(BASE_DIR), "BCA_Project")
ZIP_PATH = os.path.join(os.path.dirname(BASE_DIR), "BCA_Project.zip")

def export_project():
    print(f"[INFO] Exporting project from: {SOURCE_DIR}")
    print(f"[INFO] Target Desktop folder:  {TARGET_DIR}")
    
    # 1. Prepare target directory
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Existing {TARGET_DIR} found. Cleaning up...")
        shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Folders to copy completely
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
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git*")
            )

    # Copy scratch/eval_dataset (omit large redundant archive scratch/soybean_dataset.zip)
    src_eval = os.path.join(SOURCE_DIR, "scratch", "eval_dataset")
    dst_eval = os.path.join(TARGET_DIR, "scratch", "eval_dataset")
    if os.path.exists(src_eval):
        print("  -> Copying scratch/eval_dataset (OOD benchmarks)...")
        shutil.copytree(src_eval, dst_eval, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # Files to copy
    files = [
        ".env",
        ".env.example",
        ".gitignore",
        "app.py",
        "config.py",
        "predict_sample.py",
        "prepare_samples.py",
        "README.md",
        "requirements.txt",
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

    # Create convenient run_project.bat
    bat_content = """@echo off
title Smart Crop AI - BCA Project
echo ======================================================================
echo           SMART CROP AI: CROP DISEASE & RECOMMENDATION SYSTEM
echo                           BCA FINAL PROJECT
echo ======================================================================
echo.
echo [1/3] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in system PATH.
    echo Please install Python 3.8+ or add it to PATH.
    pause
    exit /b
)

python -c "import flask, tensorflow, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] Installing required packages from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo [2/3] Core dependencies verified.
)

echo.
echo [3/3] Launching Flask Web Application on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this terminal to stop the application.
echo.
python app.py
pause
"""
    bat_path = os.path.join(TARGET_DIR, "run_project.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print("  -> Created run_project.bat launcher.")

    # Create run_tests.bat
    test_bat_content = """@echo off
title Run Verification Tests - BCA Project
echo ======================================================================
echo                  RUNNING AUTOMATED TEST SUITE
echo ======================================================================
python -m unittest test_app.py
echo.
echo Running comprehensive pipeline verification:
python training/comprehensive_verification.py
pause
"""
    with open(os.path.join(TARGET_DIR, "run_tests.bat"), "w", encoding="utf-8") as f:
        f.write(test_bat_content)
    print("  -> Created run_tests.bat launcher.")

    print(f"\n[SUCCESS] Successfully exported BCA_Project folder to: {TARGET_DIR}")

    # Create ZIP archive
    print(f"\n[INFO] Creating ZIP archive: {ZIP_PATH} ...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, filenames in os.walk(TARGET_DIR):
            for file in filenames:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(TARGET_DIR))
                zipf.write(file_path, rel_path)

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[SUCCESS] Created ZIP archive: {ZIP_PATH} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    export_project()
