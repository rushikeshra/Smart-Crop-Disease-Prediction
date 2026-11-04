# Project Overview: Smart Crop Disease Prediction and Crop Recommendation System

## 1. Introduction
Agriculture is the backbone of the global economy and food security. However, smallholder farmers face two critical challenges:
1. **Crop Selection Risk**: Choosing suboptimal crops that fail to align with soil fertility and local rainfall.
2. **Crop Disease Losses**: Uncontrolled plant foliar diseases leading to 20%–40% loss in harvest yield due to delayed diagnosis and incorrect pesticide application.

The **Smart Crop Disease Prediction and Crop Recommendation System** is an end-to-end full-stack Artificial Intelligence decision-support platform designed to solve these exact problems.

---

## 2. Core Modules & Problem Solved

| Module | Purpose | Input | AI/ML Technology | Output |
| :--- | :--- | :--- | :--- | :--- |
| **Module A: Crop Disease Prediction** | Diagnose foliage diseases early and recommend organic/chemical treatments | Leaf Photograph (JPG/PNG) | **MobileNetV2 Transfer Learning (CNN)** | Crop Name, Disease, Confidence, Symptoms, Pathogen, Treatments, Prevention |
| **Module B: Crop Recommendation** | Predict the highest-yielding crop for specific field parameters | Soil $N, P, K$, Temp, Humidity, pH, Rainfall | **Random Forest Classifier (Ensemble ML)** | Recommended Crop, Top 3 Candidates, Cultivation Guide, Irrigation Needs |

---

## 3. Key Differentiators & Highlights
- **Dual-Model Synergy**: Integrates both deep learning computer vision (MobileNetV2 CNN) and tabular agronomic machine learning (Random Forest) under a unified dashboard.
- **Vetted Agronomic Knowledge Base**: Comprehensive remedies covering 16 crop disease and healthy foliage classes across 7 crops, plus detailed cultivation guides for 22 crops.
- **Audit & History Logging**: All scans and recommendation inputs are permanently stored in MySQL database (with automated SQLite fallback for local demo) with user-isolated history.
- **Fast & Responsive UI**: Built with Flask, Jinja2 templates, Bootstrap 5, and vanilla JavaScript for clean, responsive leaf uploads and soil analysis forms.
- **Reliable Security**: Passwords salted and hashed with PBKDF2/SHA256 via Werkzeug, secure HTTP session cookies, and strict file validation.
