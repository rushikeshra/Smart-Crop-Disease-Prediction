import os
import sys
import json
import urllib.request
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "dataset", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

def download_github_folder(repo, folder_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    url = f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(folder_path)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            items = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error listing {repo}/{folder_path}: {e}")
        return 0

    downloaded = 0
    for item in items:
        if item.get("type") == "file" and item.get("download_url"):
            fname = item["name"]
            if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue
            dest_file = os.path.join(target_dir, fname)
            if os.path.exists(dest_file):
                downloaded += 1
                continue
            try:
                img_req = urllib.request.Request(item["download_url"], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    content = img_resp.read()
                with open(dest_file, "wb") as f:
                    f.write(content)
                with Image.open(dest_file) as img:
                    img.verify()
                downloaded += 1
            except Exception as e:
                print(f"  [WARN] Failed {fname}: {e}")
                if os.path.exists(dest_file):
                    os.remove(dest_file)
    print(f"[{repo}/{folder_path}] -> Downloaded {downloaded} valid images into {target_dir}")
    return downloaded

if __name__ == "__main__":
    print("Testing download of cotton and pigeon pea datasets...")
    # 1. Cotton Bacterial Blight
    c_bb = os.path.join(RAW_DIR, "Cotton___Bacterial_blight")
    download_github_folder("AiJared/Cotton-Plant-Disease-Detection", "cotton-plant-disease-data/Bacterial Blight", c_bb)

    # 2. Cotton Healthy
    c_hl = os.path.join(RAW_DIR, "Cotton___healthy")
    download_github_folder("AiJared/Cotton-Plant-Disease-Detection", "cotton-plant-disease-data/Healthy leaf", c_hl)

    # 3. Cotton Alternaria / Target Spot
    c_ts = os.path.join(RAW_DIR, "Cotton___Alternaria_leaf_spot")
    download_github_folder("AiJared/Cotton-Plant-Disease-Detection", "cotton-plant-disease-data/Target spot", c_ts)

    # 4. Cotton Leaf Curl / Powdery Mildew
    c_pm = os.path.join(RAW_DIR, "Cotton___Leaf_curl_virus")
    download_github_folder("AiJared/Cotton-Plant-Disease-Detection", "cotton-plant-disease-data/Powdery Mildew", c_pm)

    # 5. Pigeon Pea leaves from Sakshiwanode
    p_dir = os.path.join(RAW_DIR, "pigeon_pea_raw_pool")
    download_github_folder("Sakshiwanode/Pigeon_pea_unhealthyleaf_dataset", "Pigeon pea", p_dir)
