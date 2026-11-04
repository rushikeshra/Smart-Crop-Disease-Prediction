# AGENTS.md — Persistent Project Memory & Architecture Guide

## 1. Project Identity & Purpose
- **Project Name:** Smart Crop AI (BCA Final Project)
- **Primary Mission:** High-precision agricultural crop disease detection with strict out-of-distribution (OOD) rejection and precision crop recommendation.
- **Key Invariant:** Never force an unsupported crop or an uncataloged condition into an unrelated disease diagnosis. Zero false diagnoses.

---

## 2. Environment & Execution Context
- **Operating System:** Windows 11 / x64
- **Working Python Interpreter:** Python 3.8 (Located at `C:\Users\ASUS\AppData\Local\Programs\Python\Python38\python.exe` or system PATH `python`).
- **Caution:** Do NOT invoke Python 3.11 (`Python311\python.exe`) directly — dependencies (`flask`, `tensorflow`, `scikit-learn`, `pillow`) are installed exclusively in the Python 3.8 environment.
- **Desktop Export:** `C:\Users\ASUS\OneDrive\Desktop\BCA_Project` and `C:\Users\ASUS\OneDrive\Desktop\BCA_Project.zip`.

---

## 3. Supported Crops (10 Crops) & Diseases (31 Classes)

### Supported Crops:
1. **Apple** (*Malus domestica*)
2. **Bell Pepper** (*Capsicum annuum*)
3. **Corn / Maize** (*Zea mays*)
4. **Cotton** (*Gossypium spp.*) — **Full Disease Support**
5. **Grape** (*Vitis vinifera*)
6. **Green Gram** (*Vigna radiata*) — **Full Disease Support**
7. **Pigeon Pea** (*Cajanus cajan*) — **Full Disease Support**
8. **Potato** (*Solanum tuberosum*)
9. **Soybean** (*Glycine max*) — **Full Disease Support**
10. **Tomato** (*Solanum lycopersicum*)

### Complete 31-Class Disease Catalog:
- `Apple___Apple_scab` (*Venturia inaequalis*)
- `Apple___Black_rot` (*Botryosphaeria obtusa*)
- `Apple___healthy`
- `Corn_(maize)___Common_rust_` (*Puccinia sorghi*)
- `Corn_(maize)___healthy`
- `Cotton___Alternaria_leaf_spot` (*Alternaria macrospora*)
- `Cotton___Bacterial_blight` (*Xanthomonas citri*)
- `Cotton___Leaf_curl_virus` (*CLCuD*)
- `Cotton___healthy`
- `Grape___Black_rot` (*Guignardia bidwellii*)
- `Grape___healthy`
- `Green_Gram___Cercospora_leaf_spot` (*Cercospora canescens*)
- `Green_Gram___Powdery_mildew` (*Erysiphe polygoni*)
- `Green_Gram___Yellow_mosaic` (*MYMV*)
- `Green_Gram___healthy`
- `Pepper__bell___Bacterial_spot` (*Xanthomonas campestris*)
- `Pepper__bell___healthy`
- `Pigeon_Pea___Cercospora_leaf_spot` (*Cercospora indica*)
- `Pigeon_Pea___Phytophthora_blight` (*Phytophthora cajani*)
- `Pigeon_Pea___Sterility_mosaic` (*PPSMV*)
- `Pigeon_Pea___healthy`
- `Potato___Early_blight` (*Alternaria solani*)
- `Potato___Late_blight` (*Phytophthora infestans*)
- `Potato___healthy`
- `Soybean___Bacterial_blight` (*Pseudomonas savastanoi pv. glycinea*) — [ASDID Dataset]
- `Soybean___Frogeye_leaf_spot` (*Cercospora sojina*) — [ASDID Dataset]
- `Soybean___Soybean_rust` (*Phakopsora pachyrhizi*) — [ASDID Dataset]
- `Soybean___healthy` — [PlantVillage Dataset]
- `Tomato___Early_blight` (*Alternaria solani*)
- `Tomato___Late_blight` (*Phytophthora infestans*)
- `Tomato___healthy`

---

## 4. Two-Stage Crop-Constrained Architecture (`ml/crop_validator.py`)

### Stage 1: Foliar & Morphological Integrity Gate
1. **Variance Check:** Standard deviation $< 14.0$ rejects blank, uniformly colored, or blurred images.
2. **Chlorophyll Index:** Ratio of green chloroplast pigmentation $(G > 1.04R \land G > 1.04B)$ must be $\ge 0.03$. Non-foliar objects (skin, wood, metal, plastic) are rejected.
3. **Fruit Filter:** High red/orange circular bodies with low vein edge gradients are rejected.

### Stage 2: Crop Classification & Centroid Distance OOD Gate
1. Extracts 128-d normalized embedding $\mathbf{z}$ from layer `crop_features` of `models/crop_model.keras`.
2. Computes cosine similarity to target crop centroids stored in `models/crop_centroids.json`.
3. **Multi-Prototype Soybean Centroid:**
   $$\text{Sim}(\mathbf{z}, \text{Soybean}) = \max(\cos(\mathbf{z}, \mathbf{c}_{\text{healthy}}), \cos(\mathbf{z}, \mathbf{c}_{\text{field\_disease}}))$$
   - $\mathbf{c}_{\text{healthy}}$: Derived from PlantVillage laboratory images (uniform background).
   - $\mathbf{c}_{\text{field\_disease}}$: Derived from Auburn Soybean Disease Image Dataset (ASDID) natural canopy images.
4. **Calibrated OOD Thresholds:**
   - `Apple`: 0.629
   - `Bell_Pepper`: 0.550 (Rejects Rice at 0.529 while accepting 100% of pepper leaves)
   - `Corn`: 0.740 (Rejects Wheat at 0.744)
   - `Grape`: 0.760
   - `Potato`: 0.625
   - `Soybean`: 0.620 (Rejects Rice/Wheat while accepting 100% of healthy and diseased soybean)
   - `Tomato`: 0.593

### Stage 3: Crop-Constrained Softmax Re-Normalization
- Once crop $C$ is validated, disease logits from `models/disease_model.keras` are sliced strictly to the subset of classes belonging to crop $C$.
- Softmax is re-normalized over only the allowed disease classes for that crop.
- Combined confidence: $P(\text{crop}) \times P(\text{disease} \mid \text{crop})$.
- **Soybean Ambiguity Guard:** If top sub-confidence $< 0.40$ or sum of soybean activations $< 0.15$, returns:
  `"Soybean detected, but disease could not be reliably identified."`

---

## 5. Key Empirical Benchmarks
- **Disease Model Accuracy:** **94.88%** on 723 independent test images (Macro F1: **94.93%**).
- **Crop Classifier Accuracy:** **97.65%** on independent test set.
- **User Uploaded Leaf (`leaf_c141119cad69.jpg`):** Diagnosed as **Soybean (*Glycine max*) — Bacterial Blight (*Pseudomonas savastanoi*)** with **67.65%** confidence.
- **Out-of-Distribution Rejection:** 100% on Rice, Wheat, Fruits, and Non-leaf objects.

---

## 6. Commands to Run
```bash
# Start Flask Dev Server (runs on http://127.0.0.1:5000)
python app.py

# Run Full Unit Test Suite (13 tests)
python -m unittest test_app.py

# Run Multi-Image Pipeline Verification (13 test cases)
python training/comprehensive_verification.py

# Re-export to Desktop
python training/export_bca_project.py
```
