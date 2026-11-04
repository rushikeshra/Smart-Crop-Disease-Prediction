import os
import sys
import json

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db import init_db, get_disease_recommendation

def seed_database():
    print("=" * 70)
    print("SEEDING & VERIFYING SMART CROP DATABASE")
    print("=" * 70)
    
    success = init_db()
    if not success:
        print("[ERROR] Database initialization failed. Ensure MySQL is running on port 3306.")
        return False

    # Check knowledge base
    disease_json = os.path.join(os.path.dirname(__file__), "disease_info.json")
    if not os.path.exists(disease_json):
        print(f"[ERROR] disease_info.json not found at {disease_json}")
        return False

    with open(disease_json, "r", encoding="utf-8") as f:
        diseases = json.load(f)

    print(f"[SUCCESS] Loaded {len(diseases)} structured crop disease recommendation profiles:")
    for idx, (cls_name, info) in enumerate(diseases.items(), start=1):
        print(f"  {idx:>2}. [{info['crop_name']}] -> {info['disease_name']}")

    print("=" * 70)
    print("[SUCCESS] MySQL database schema and disease knowledge base ready.")
    return True

if __name__ == "__main__":
    seed_database()
