import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = BASE_DIR
DESKTOP_DIR = os.path.dirname(BASE_DIR)

TARGET_DIR = os.path.join(DESKTOP_DIR, "My-Project")
ZIP_PATH = os.path.join(DESKTOP_DIR, "My-Project.zip")

def export_my_project():
    print(f"[INFO] Exporting project from: {SOURCE_DIR}")
    print(f"[INFO] Target Desktop folder:  {TARGET_DIR}")
    print(f"[INFO] Target Desktop zip:     {ZIP_PATH}")

    # 1. Prepare target directory
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Existing {TARGET_DIR} found. Cleaning up...")
        shutil.rmtree(TARGET_DIR, ignore_errors=True)
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
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git*", "*.db", "*.sqlite*", "raw")
            )

    # Copy scratch/eval_dataset if present (benchmarks)
    src_eval = os.path.join(SOURCE_DIR, "scratch", "eval_dataset")
    dst_eval = os.path.join(TARGET_DIR, "scratch", "eval_dataset")
    if os.path.exists(src_eval):
        print("  -> Copying scratch/eval_dataset...")
        shutil.copytree(src_eval, dst_eval, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # 3. Files to copy
    files = [
        ".env.example",
        ".gitignore",
        "AGENTS.md",
        "app.py",
        "config.py",
        "predict_sample.py",
        "prepare_samples.py",
        "README.md",
        "requirements.txt",
        "SAMPLE_LEAF_IMAGES_GUIDE.md",
        "test_app.py",
        "run.bat"
    ]

    for f in files:
        src = os.path.join(SOURCE_DIR, f)
        dst = os.path.join(TARGET_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  -> Copied file: {f}")

    # Copy .env if available, or generate from .env.example
    env_src = os.path.join(SOURCE_DIR, ".env")
    if os.path.exists(env_src):
        shutil.copy2(env_src, os.path.join(TARGET_DIR, ".env"))

    # 4. Copy working virtual environment (.venv) so python app.py runs out-of-the-box
    src_venv = os.path.join(SOURCE_DIR, ".venv")
    dst_venv = os.path.join(TARGET_DIR, ".venv")
    if os.path.exists(src_venv):
        print("  -> Copying working .venv environment to My-Project...")
        shutil.copytree(src_venv, dst_venv, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # 5. Create python.bat wrapper in My-Project
    # Ensures typing 'python app.py' in Windows cmd automatically routes to .venv
    py_bat_content = """@echo off
if exist "%~dp0.venv\\Scripts\\python.exe" (
    "%~dp0.venv\\Scripts\\python.exe" %*
) else (
    python.exe %*
)
"""
    with open(os.path.join(TARGET_DIR, "python.bat"), "w", encoding="utf-8") as f:
        f.write(py_bat_content)
    print("  -> Created python.bat wrapper.")

    # 6. Create 1-click run_project.bat
    bat_content = """@echo off
title Smart Crop AI - My-Project
echo ======================================================================
echo           SMART CROP AI: CROP DISEASE & RECOMMENDATION SYSTEM
echo ======================================================================
echo.
echo Launching Flask Web Application on http://127.0.0.1:5000 ...
if exist "%~dp0.venv\\Scripts\\python.exe" (
    "%~dp0.venv\\Scripts\\python.exe" app.py
) else (
    python app.py
)
pause
"""
    with open(os.path.join(TARGET_DIR, "run_project.bat"), "w", encoding="utf-8") as f:
        f.write(bat_content)
    print("  -> Created run_project.bat launcher.")

    # Create run_tests.bat
    test_bat_content = """@echo off
title Run Verification Tests - My-Project
echo ======================================================================
echo                  RUNNING AUTOMATED TEST SUITE
echo ======================================================================
if exist "%~dp0.venv\\Scripts\\python.exe" (
    "%~dp0.venv\\Scripts\\python.exe" -m unittest test_app.py
) else (
    python -m unittest test_app.py
)
pause
"""
    with open(os.path.join(TARGET_DIR, "run_tests.bat"), "w", encoding="utf-8") as f:
        f.write(test_bat_content)
    print("  -> Created run_tests.bat launcher.")

    print(f"\n[SUCCESS] Successfully exported My-Project folder to: {TARGET_DIR}")

    # 7. Create ZIP archive (omit .venv from zip to keep it lightweight)
    print(f"\n[INFO] Creating ZIP archive: {ZIP_PATH} ...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, filenames in os.walk(TARGET_DIR):
            if ".venv" in root:
                continue
            for file in filenames:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(TARGET_DIR))
                zipf.write(file_path, rel_path)

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[SUCCESS] Created ZIP archive: {ZIP_PATH} ({zip_size_mb:.2f} MB)")


if __name__ == "__main__":
    export_my_project()
