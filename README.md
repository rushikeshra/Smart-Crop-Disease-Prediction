# Smart Crop Disease Prediction and Crop Recommendation System

A comprehensive, academic-grade Machine Learning and Web Application designed for smallholder farmers, agricultural extension officers, and agronomy students. The system integrates two core AI capabilities:
1. **Leaf Disease Prediction**: Real-time foliar disease classification from uploaded leaf photos using a MobileNetV2 Convolutional Neural Network (CNN).
2. **Precision Crop Recommendation**: Multi-class tabular soil-to-crop suitability recommendation using an ensemble Random Forest model.

---

## 1. Features

1. **User Registration & Authentication**:
   - Secure account registration with email validation.
   - Cryptographic password hashing (PBKDF2-HMAC-SHA256 via Werkzeug).
   - Tamper-proof HTTP session cookies with complete user data isolation.

2. **Leaf Crop Disease Prediction**:
   - Clean drag-and-drop leaf photo upload interface with client-side preview.
   - MobileNetV2 Deep Learning inference supporting **16 disease and healthy foliage classes** across **7 major crops**.
   - Strict confidence threshold guard (< 60% warning) preventing misdiagnoses on ambiguous photos.
   - Structured agronomic recommendations: biological controls, cultural prevention, and fungicide active ingredients.
   - Printable diagnosis advisory reports (`@media print` formatted).

3. **Precision Crop Recommendation**:
   - Form-based input for 7 soil and climatic parameters ($N, P, K$, Temperature, Humidity, pH, Rainfall).
   - Fast demo presets (Rice, Maize, Coffee) for instantaneous demonstration.
   - Random Forest model predicts primary recommended crop and top-3 ranked alternatives.
   - Complete agronomic cultivation profile: soil requirements, sowing techniques, water needs, harvest duration, and farming tips.

4. **Leaf Disease Diagnosis History**:
   - Complete historical log of all past leaf diagnoses with photo thumbnails, confidence percentages, and timestamps.

5. **Crop Recommendation History**:
   - User-isolated log of past soil analyses and predicted crops.

6. **Interactive Dashboard**:
   - Summary diagnostic statistics, total scans, total soil analyses, and recent activity feeds.

7. **Database Storage with Zero-Crash Fallback**:
   - Standard relational persistence with PyMySQL for MySQL 8.0+ / MariaDB.
   - Automatic local SQLite fallback (`database/smart_crop.db`) if MySQL is offline.

---

## 2. Machine Learning Models

### A. Crop Leaf Disease Prediction Model
- **Algorithm**: Convolutional Neural Network (MobileNetV2 Transfer Learning).
- **Pretrained Base**: ImageNet feature weights with fine-tuned top dense layers.
- **Input Dimensions**: $224 \times 224 \times 3$ RGB.
- **Output Classes**: Exactly **16 classes** across **7 crops**:
  1. `Apple___Apple_scab`
  2. `Apple___Black_rot`
  3. `Apple___healthy`
  4. `Corn_(maize)___Common_rust_`
  5. `Corn_(maize)___healthy`
  6. `Grape___Black_rot`
  7. `Grape___healthy`
  8. `Pepper__bell___Bacterial_spot`
  9. `Pepper__bell___healthy`
  10. `Potato___Early_blight`
  11. `Potato___Late_blight`
  12. `Potato___healthy`
  13. `Soybean___healthy`
  14. `Tomato___Early_blight`
  15. `Tomato___Late_blight`
  16. `Tomato___healthy`
- **Evaluated Test Metrics (519 Test Images in `models/evaluation_metrics.json`)**:
  - **Accuracy**: **96.34%**
  - **Macro Precision**: **96.40%**
  - **Macro Recall**: **96.33%**
  - **Macro F1-Score**: **96.32%**

### B. Crop Recommendation Model
- **Algorithm**: Random Forest Classifier ($n_{\text{estimators}} = 100$).
- **Input Parameters (7 features)**:
  1. Nitrogen ($N$ in soil)
  2. Phosphorus ($P$ in soil)
  3. Potassium ($K$ in soil)
  4. Temperature ($^\circ$C)
  5. Relative Humidity ($\%$)
  6. Soil pH ($0-14$)
  7. Rainfall (mm)
- **Output Classes**: **22 Crops** (Rice, Maize, Chickpea, Kidneybeans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee).
- **Evaluated Test Metrics (440 Test Samples in `ml/crop_recommendation/model/metrics.json`)**:
  - **Accuracy**: **98.86%**
  - **Macro Precision**: **98.87%**
  - **Macro Recall**: **98.86%**
  - **Macro F1-Score**: **98.86%**

---

## 3. Technology Stack

- **Backend**: Python 3.8 - 3.11, Flask 3.0+, Werkzeug (Security & Password Hashing).
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Bootstrap 5, FontAwesome Icons.
- **Machine Learning**: TensorFlow 2.13+, Keras, scikit-learn, NumPy, Pandas, Pillow, Joblib.
- **Database**: MySQL 8.0+ / MariaDB (via PyMySQL) with automatic SQLite local fallback.

---

## 4. Final Project Structure

```
smart-crop-system/
│
├── app.py                             # Flask Application entrypoint & all route handlers
├── config.py                          # Central configuration & parameters
├── requirements.txt                   # Python package dependencies
├── .env.example                       # Environment variables template
├── .env                               # Local environment variables
├── test_app.py                        # Automated unit & integration test suite (9 tests)
├── predict_sample.py                  # CLI single-leaf inference tool
├── prepare_samples.py                 # CLI multi-crop verification tool (14 sample images)
├── README.md                          # Comprehensive documentation & run guide
├── VIVA_QUESTIONS_GUIDE.md            # Academic viva preparation Q&A guide
├── SAMPLE_LEAF_IMAGES_GUIDE.md        # Verified sample leaf images test guide
│
├── dataset/                           # Dataset directory
│   ├── crop_recommendation.csv        # 2,200 records soil-crop tabular dataset
│   ├── sample_leaves/                 # Benchmark test images
│   └── processed/                     # Stratified splits (16 classes)
│       ├── train/                     # 2,416 images
│       ├── val/                       # 517 images
│       └── test/                      # 519 images
│
├── training/                          # Official Disease Model Training Pipeline
│   ├── inspect_dataset.py             # Dataset audit & corruption inspection
│   ├── prepare_dataset.py             # Stratified dataset split & deduplication
│   ├── train.py                       # Official MobileNetV2 16-class training script
│   └── evaluate.py                    # Evaluation metrics & confusion matrix generator
│
├── models/                            # Active Trained Models & Evaluation
│   ├── disease_model.keras            # Official trained MobileNetV2 CNN model
│   ├── disease_model.h5               # Fallback HDF5 model
│   ├── class_names.json               # Authoritative 16-class mapping
│   ├── evaluation_metrics.json        # Test evaluation report (96.34% accuracy)
│   └── training_history.json          # Loss and accuracy history per epoch
│
├── ml/                                # Machine Learning Modules
│   ├── test_models.py                 # Direct test runner for both ML models
│   └── crop_recommendation/           # Official Crop Recommendation Module
│       ├── train.py                   # Random Forest training script
│       ├── predict.py                 # Crop recommendation inference class
│       ├── preprocessing.py           # Agronomic limit validation & scaler
│       ├── generate_dataset.py        # Dataset utility
│       └── model/
│           ├── crop_recommendation_rf.joblib # Trained Random Forest model
│           ├── crop_scaler.joblib            # Trained feature scaler
│           └── metrics.json                  # Evaluated metrics (98.86% accuracy)
│
├── database/                          # Database Connection & Seed Data
│   ├── schema.sql                     # MySQL / SQLite DDL schema
│   ├── db.py                          # PyMySQL connection & CRUD queries layer
│   ├── disease_info.json              # Pathology knowledge base (treatments & cures)
│   ├── seed_data.py                   # Agronomic profiles for 22 crops
│   ├── seed_diseases.py               # Table seeder script
│   └── smart_crop.db                  # Local SQLite database (auto-created)
│
├── sample_crop_images/                # 14 curated verified leaf images (2 per crop)
├── static/                            # Web Static Assets
│   ├── css/style.css                  # Custom agricultural CSS stylesheet
│   ├── js/main.js                     # Upload dropzone & client preview handler
│   ├── images/                        # Confusion matrix & training curve charts
│   └── uploads/                       # User-uploaded leaf photos
│
├── templates/                         # Jinja2 HTML Templates
│   ├── base.html                      # Navbar, flash messages, footer layout
│   ├── index.html                     # Hero landing page
│   ├── register.html                  # User registration
│   ├── login.html                     # User authentication
│   ├── dashboard.html                 # Farmer diagnostic dashboard
│   ├── predict.html                   # Leaf photo upload dropzone
│   ├── result.html                    # Disease diagnosis report & print view
│   ├── history.html                   # Disease diagnosis history table
│   ├── crop_recommendation.html       # Soil & climate input form
│   ├── crop_result.html               # Crop recommendation result & cultivation guide
│   ├── crop_history.html              # Soil analysis history table
│   ├── 404.html                       # 404 not found page
│   └── 500.html                       # 500 internal server error page
│
└── docs/                              # Academic Project Documentation
    ├── project-overview.md            # Project scope & problem definition
    ├── system-architecture.md         # MVC system architecture & Mermaid diagrams
    ├── system-requirements.md         # Hardware & software SRS
    ├── ml-models.md                   # Mathematical formulation & model metrics
    ├── database-design.md             # ER diagrams & schema dictionary
    ├── testing.md                     # QA test cases & execution matrix
    ├── api-documentation.md           # Web routes & REST API endpoints
    └── viva-questions.md              # Viva voce Q&A preparation
```

---

## 5. Step-by-Step Setup & Run Guide

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(If MySQL is not installed, the application automatically uses SQLite so you can test immediately with zero configuration).*

### Step 3: Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. How to Run Model Predictions from Command Line

### Test Both Models Directly:
```bash
python ml/test_models.py
```

### Test All 14 Desktop Sample Leaf Images:
```bash
python prepare_samples.py
```

### Run Single Leaf Diagnosis:
```bash
python predict_sample.py --image sample_crop_images/tomato_sample_1_early_blight.jpg
```

---

## 7. How to Run Automated Unit Tests

Run the complete 9-test test suite covering authentication, user isolation, image upload validation, model predictions, and database persistence:
```bash
python test_app.py
```

