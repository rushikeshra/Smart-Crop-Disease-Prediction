import os
import sys
import json
import shutil
import zipfile
from PIL import Image

def main():
    print("=" * 80)
    print("INTEGRATING SOYBEAN LEAF DISEASE DATASET")
    print("=" * 80)
    
    zip_path = os.path.join("scratch", "soybean_dataset.zip")
    if not os.path.exists(zip_path):
        print(f"Error: Dataset archive not found at {zip_path}")
        return

    base_dataset = os.path.join("dataset", "processed")
    split_map = {
        "train": "train",
        "vald": "val",
        "test": "test"
    }

    class_map = {
        "bacterial_blight": "Soybean___Bacterial_blight",
        "frogeye": "Soybean___Frogeye_leaf_spot",
        "soybean_rust": "Soybean___Soybean_rust"
    }

    extracted_counts = {}

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        for name in namelist:
            parts = name.split("/")
            if len(parts) >= 3 and parts[-1].lower().endswith((".jpg", ".jpeg", ".png")):
                orig_split = parts[0]
                orig_cls = parts[1]
                fname = parts[-1]

                if orig_split not in split_map or orig_cls not in class_map:
                    continue

                target_split = split_map[orig_split]
                target_cls = class_map[orig_cls]
                target_dir = os.path.join(base_dataset, target_split, target_cls)
                os.makedirs(target_dir, exist_ok=True)

                target_path = os.path.join(target_dir, fname)

                # Extract and verify image integrity
                with zf.open(name) as src_file:
                    img_data = src_file.read()
                    with open(target_path, "wb") as dst_file:
                        dst_file.write(img_data)

                # Verify PIL read
                try:
                    with Image.open(target_path) as im:
                        im.verify()
                    key = f"{target_split}/{target_cls}"
                    extracted_counts[key] = extracted_counts.get(key, 0) + 1
                except Exception as e:
                    print(f"Corrupted image skipped: {name} ({e})")
                    if os.path.exists(target_path):
                        os.remove(target_path)

    print("\nExtraction & Verification Complete:")
    for k in sorted(extracted_counts.keys()):
        print(f"  {k:35s}: {extracted_counts[k]} images")

    # ------------------------------------------------------------------
    # Update database/disease_info.json with soybean disease entries
    # ------------------------------------------------------------------
    disease_info_path = os.path.join("database", "disease_info.json")
    with open(disease_info_path, "r", encoding="utf-8") as f:
        disease_info = json.load(f)

    soybean_diseases = {
        "Soybean___Bacterial_blight": {
            "class_name": "Soybean___Bacterial_blight",
            "crop_name": "Soybean (Glycine max)",
            "disease_name": "Bacterial Blight (Pseudomonas savastanoi pv. glycinea)",
            "description": "Bacterial blight is a widespread foliar disease of soybean favored by cool, rainy, and windy conditions. Lesions start as angular water-soaked spots that turn dark brown to black surrounded by a chlorotic yellow halo.",
            "symptoms": [
                "Small, angular, translucent water-soaked spots on young leaves.",
                "Lesions turn reddish-brown to black, surrounded by distinct yellow halos.",
                "Lesion centers frequently tear and fall out, giving leaves a tattered or ragged appearance.",
                "In severe cases, premature defoliation occurs in the upper canopy."
            ],
            "prevention": [
                "Plant high-quality, certified disease-free soybean seed and blight-tolerant varieties.",
                "Practice a 1-to-2 year crop rotation with non-host crops such as corn, wheat, or sorghum.",
                "Avoid cultivating or moving farm machinery through soybean fields when foliage is wet.",
                "Incorporate crop residue into the soil after harvest to accelerate bacterial decomposition."
            ],
            "treatment_or_cure": [
                "Copper-based bactericides (e.g., copper hydroxide, copper oxychloride) may reduce bacterial spread if applied early during cool, wet periods.",
                "Biological control agents containing Bacillus subtilis or Bacillus amyloliquefaciens can suppress bacterial colonization."
            ],
            "chemical_information": "Copper hydroxide or copper sulfate formulations labeled for soybean foliar application. Note: Repeated copper applications can cause phytotoxicity under hot conditions. Consult local extension recommendations.",
            "disclaimer": "Fungicides targeting fungal pathogens are ineffective against bacterial blight. Ensure accurate diagnosis before chemical application."
        },
        "Soybean___Frogeye_leaf_spot": {
            "class_name": "Soybean___Frogeye_leaf_spot",
            "crop_name": "Soybean (Glycine max)",
            "disease_name": "Frogeye Leaf Spot (Cercospora sojina)",
            "description": "Frogeye leaf spot is a destructive foliar fungal disease causing circular to angular lesions with tan-to-gray centers and narrow dark reddish-brown borders. Severe infection causes premature senescence and substantial yield loss during pod-fill.",
            "symptoms": [
                "Small, dark, water-soaked circular spots on upper leaf surfaces that quickly turn brown.",
                "Mature lesions have light gray or tan centers surrounded by a prominent dark reddish-purple or brown margin (the classic 'frog-eye' appearance).",
                "Minute dark gray fungal tufts (conidiophores) are visible in lesion centers under magnification on leaf undersides.",
                "Extensive lesions coalesce causing blight, leaf yellowing, and premature leaf drop."
            ],
            "prevention": [
                "Select soybean varieties with high resistance (possessing Rcs resistance genes such as Rcs3).",
                "Rotate crops with non-host crops (corn, cotton, small grains) for at least 1-2 years.",
                "Deep-till or bury crop residue after harvest to reduce fungal spore overwintering in debris."
            ],
            "treatment_or_cure": [
                "Apply preventative or curative foliar fungicides at the R3 (beginning pod) to R4 (full pod) development stages.",
                "Scout fields beginning at flowering (R1), particularly in warm, humid weather with frequent rainfall."
            ],
            "chemical_information": "Foliar fungicides featuring multi-mode of action premixes: Triazoles (DMI: Prothioconazole, Difenoconazole, Tebuconazole) combined with Succinate Dehydrogenase Inhibitors (SDHI: Fluxapyroxad, Benzovindiflupyr) or Strobilurins (QoI: Azoxystrobin, Pyraclostrobin). Note: Quinone Outside Inhibitor (QoI / strobilurin) resistance has been confirmed in multiple regions; use premixes with DMIs or SDHIs.",
            "disclaimer": "Always rotate fungicide modes of action (FRAC groups) to prevent fungicide resistance development."
        },
        "Soybean___Soybean_rust": {
            "class_name": "Soybean___Soybean_rust",
            "crop_name": "Soybean (Glycine max)",
            "disease_name": "Asian Soybean Rust (Phakopsora pachyrhizi)",
            "description": "Asian Soybean Rust is one of the most aggressive and economically damaging soybean diseases worldwide. It causes rapid defoliation and can cause yield losses exceeding 50% to 80% if untreated during reproductive growth stages.",
            "symptoms": [
                "Tiny, chlorotic (yellow) pinhead-sized flecks on upper leaf surfaces, most concentrated in the lower canopy initially.",
                "Eruption of raised, volcano-shaped pustules (uredinia) on the undersides of leaves releasing tan, powdery spores.",
                "Pustules darken from tan to reddish-brown as lesions age.",
                "Rapid yellowing of the entire canopy followed by severe, early defoliation within days under favorable humid conditions."
            ],
            "prevention": [
                "Plant early-maturing soybean varieties to escape peak spore dispersal periods.",
                "Monitor regional soybean rust sentinel plot tracking systems and spore traps.",
                "Eradicate overwintering alternate host plants (especially Kudzu / Pueraria montana) near field perimeters."
            ],
            "treatment_or_cure": [
                "Apply foliar fungicide promptly upon disease detection or when local alert systems indicate spores are active in the region.",
                "Fungicide timing is critical: sprays applied after defoliation exceeds 10% provide diminished economic return."
            ],
            "chemical_information": "Fungicide tank mixes or premixes containing DMI triazoles (e.g., Flutriafol, Prothioconazole, Tebuconazole) + SDHIs (e.g., Fluxapyroxad, Benzovindiflupyr) + protective multi-site fungicides (e.g., Chlorothalonil, Mancozeb). Follow FRAC resistance guidelines.",
            "disclaimer": "Asian soybean rust is an obligate biotrophic pathogen. Fungicides must be applied before widespread infection takes hold."
        }
    }

    for k, v in soybean_diseases.items():
        disease_info[k] = v

    with open(disease_info_path, "w", encoding="utf-8") as f:
        json.dump(disease_info, f, indent=2)

    print(f"\nUpdated {disease_info_path} with 3 new soybean disease entries.")
    print("New total classes in disease_info.json:", len(disease_info))

    # ------------------------------------------------------------------
    # Summary of Total Dataset Counts
    # ------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("DATASET CLASS SUMMARY ACROSS SPLITS")
    print("=" * 80)
    for split in ["train", "val", "test"]:
        s_dir = os.path.join(base_dataset, split)
        classes = sorted(os.listdir(s_dir))
        soy_classes = [c for c in classes if c.startswith("Soybean")]
        print(f"\n--- {split.upper()} SET --- (Total Classes: {len(classes)})")
        for sc in soy_classes:
            cnt = len([f for f in os.listdir(os.path.join(s_dir, sc)) if f.lower().endswith(('.jpg','.jpeg','.png'))])
            print(f"  {sc:35s}: {cnt} images")

if __name__ == "__main__":
    main()
