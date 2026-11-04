import os
import sys
import json
import urllib.request
import urllib.parse
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "scratch", "eval_dataset")

CATEGORIES = {
    "soybean_diseased": [
        "soybean leaf",
        "Glycine max leaf",
        "soybean rust",
        "Phakopsora pachyrhizi",
        "soybean field",
        "soybean foliage"
    ],
    "rice": [
        "rice leaf",
        "Oryza sativa leaf",
        "paddy leaf",
        "rice blast",
        "rice sheath",
        "rice plant leaf"
    ],
    "wheat": [
        "wheat leaf",
        "Triticum leaf",
        "wheat rust",
        "Puccinia triticina",
        "wheat stripe rust",
        "wheat crop leaf"
    ],
    "non_leaf": [
        "desk furniture",
        "keyboard computer",
        "brick wall",
        "wooden surface",
        "concrete texture",
        "printed text document"
    ],
    "fruit": [
        "red apple fruit",
        "orange citrus fruit",
        "ripe tomato fruit",
        "yellow banana fruit",
        "lemon fruit"
    ]
}

def fetch_image_urls(query, limit=12):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "SmartCropBench/1.0 (academic research validation; contact: research@smartcrop.ai)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            urls = []
            for p in data.get("query", {}).get("pages", {}).values():
                info = p.get("imageinfo", [{}])[0]
                u = info.get("url")
                if u:
                    clean = u.split("?")[0].lower()
                    if clean.endswith((".jpg", ".jpeg", ".png")):
                        safe_title = p.get("title", "img").encode("ascii", "ignore").decode("ascii")
                        urls.append((safe_title, u))
            return urls
    except Exception as e:
        print(f"[WARN] Failed query '{query}': {e}")
        return []

def download_and_verify(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "SmartCropBench/1.0 (academic research validation)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read()
            if len(content) < 2048:
                return False
            with open(out_path, "wb") as f:
                f.write(content)
        # Verify PIL open
        with Image.open(out_path) as img:
            img.verify()
        return True
    except Exception as e:
        if os.path.exists(out_path):
            try: os.remove(out_path)
            except: pass
        return False

def build_eval_dataset():
    os.makedirs(TARGET_DIR, exist_ok=True)
    summary = {}

    for cat, queries in CATEGORIES.items():
        cat_dir = os.path.join(TARGET_DIR, cat)
        os.makedirs(cat_dir, exist_ok=True)
        count = len([f for f in os.listdir(cat_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))])
        
        # If diseased soybean, include the user's uploaded diseased soybean as one guaranteed sample
        if cat == "soybean_diseased":
            user_sample = os.path.join(BASE_DIR, "static", "uploads", "leaf_c141119cad69.jpg")
            if os.path.exists(user_sample):
                dest = os.path.join(cat_dir, "sample_user_uploaded_soybean_diseased.jpg")
                if not os.path.exists(dest):
                    import shutil
                    shutil.copy2(user_sample, dest)
                    count += 1

        print(f"\n[INFO] Gathering images for category: {cat} (existing: {count})...")
        for q in queries:
            if count >= 12:
                break
            items = fetch_image_urls(q, limit=12)
            for title, u in items:
                if count >= 12:
                    break
                idx = count + 1
                target_file = os.path.join(cat_dir, f"{cat}_{idx:02d}.jpg")
                if os.path.exists(target_file):
                    continue
                success = download_and_verify(u, target_file)
                if success:
                    print(f"  + Downloaded {cat}_{idx:02d}.jpg: {title[:40]}")
                    count += 1

        summary[cat] = count
        print(f"[DONE] Category {cat}: {count} verified images ready.")

    print("\n" + "=" * 50)
    print("OOD EVALUATION DATASET READY:")
    for k, v in summary.items():
        print(f"  - {k:<20}: {v} images")
    print("=" * 50)


if __name__ == "__main__":
    build_eval_dataset()
