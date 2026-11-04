import os
import zipfile

WORKSPACE_DIR = r"C:\Users\ASUS\OneDrive\Desktop\BCA_Project"
ZIP_PATH = r"C:\Users\ASUS\OneDrive\Desktop\BCA_Project.zip"

def package_zip():
    print(f"[INFO] Packaging workspace: {WORKSPACE_DIR}")
    print(f"[INFO] Output archive: {ZIP_PATH}")

    folders_to_include = [
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
        "translations",
        "scratch/eval_dataset"
    ]

    files_to_include = [
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

    # Temporary zip
    tmp_zip = ZIP_PATH + ".tmp"
    if os.path.exists(tmp_zip):
        os.remove(tmp_zip)

    with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add root files
        for f in files_to_include:
            f_path = os.path.join(WORKSPACE_DIR, f)
            if os.path.exists(f_path):
                arcname = os.path.join("BCA_Project", f)
                zipf.write(f_path, arcname)

        # Add folders
        for folder in folders_to_include:
            f_dir = os.path.join(WORKSPACE_DIR, folder.replace("/", os.sep))
            if os.path.exists(f_dir):
                for root, dirs, files in os.walk(f_dir):
                    if "__pycache__" in root or ".git" in root:
                        continue
                    for file in files:
                        if file.endswith((".pyc", ".tmp", ".log")):
                            continue
                        full_path = os.path.join(root, file)
                        rel = os.path.relpath(full_path, WORKSPACE_DIR)
                        arcname = os.path.join("BCA_Project", rel)
                        zipf.write(full_path, arcname)

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
    print(f"[SUCCESS] Successfully updated {ZIP_PATH} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    package_zip()
