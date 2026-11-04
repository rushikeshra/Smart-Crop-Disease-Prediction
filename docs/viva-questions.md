# College Project Viva Questions & Answers

This guide is prepared specifically for BCA / B.Tech / B.Sc final-year project viva examination.

---

## 1. Project Concept & Objectives

### Q1: What is the primary objective of this project?
**Answer:** The objective is to provide an end-to-end intelligent decision-support system for agriculture containing two mandatory ML modules:
1. **Crop Disease Prediction**: Identifying plant foliar diseases from leaf photos using deep learning CNNs (MobileNetV2).
2. **Crop Recommendation**: Recommending the highest-yielding crop based on 7 soil and climatic parameters using an ensemble Random Forest model.

### Q2: Why did you choose a dual-module system instead of only disease detection?
**Answer:** In practical agriculture, farming success depends on both pre-sowing decisions (choosing the right crop for the soil) and post-sowing management (protecting plants from pathogens). Building both modules creates a complete agronomic lifecycle tool.

---

## 2. Machine Learning & Algorithms

### Q3: Why did you use Random Forest for Crop Recommendation instead of a single Decision Tree?
**Answer:** A single decision tree suffers from high variance and easily overfits training data. Random Forest is an ensemble method that builds multiple decorrelated decision trees using bootstrap aggregation (bagging) and random feature subsets. This reduces variance, prevents overfitting, and achieved an evaluated test accuracy of **98.86%** across 22 crop classes.

### Q4: What is the significance of the 7 features in Crop Recommendation?
**Answer:**
- **N (Nitrogen)**: Essential for vegetative chlorophyll and leaf growth.
- **P (Phosphorus)**: Vital for root proliferation and seed development.
- **K (Potassium)**: Regulates stomatal opening, enzyme activation, and disease resilience.
- **Temperature & Humidity**: Govern transpiration rates and photosynthesis.
- **pH**: Determines soil nutrient availability.
- **Rainfall**: Primary water source for rainfed cultivation.

### Q5: Why is Feature Scaling (`StandardScaler`) applied?
**Answer:** Features have vastly different units and scales (e.g. Rainfall up to 300 mm vs pH between 3.5 and 9.9). Scaling standardizes features to $\mu=0$ and $\sigma=1$, ensuring distance-based metrics and gradient updates are balanced.

---

## 3. Deep Learning & Computer Vision

### Q6: Why did you choose MobileNetV2 for Crop Disease Prediction?
**Answer:** Traditional CNNs like VGG16 have over 130 million parameters and are too heavy for fast web deployment. MobileNetV2 uses **depthwise separable convolutions** and **inverted residual bottlenecks**, reducing parameters to under 3.5 million while retaining over 90% top-1 accuracy on ImageNet. This allows low-latency, real-time inference on standard web servers.

### Q7: What is Transfer Learning?
**Answer:** Transfer learning is a technique where a model pre-trained on a massive dataset (ImageNet) is adapted for a specific task (Plant Disease Classification). The early layers capture general visual features (edges, textures, color gradients), while the newly trained top dense layers learn plant disease specific features.

### Q8: What does the Softmax function do in the output layer?
**Answer:** Softmax converts raw logit outputs $z_i$ into a normalized probability distribution across all $K$ classes:
$$\sigma(\mathbf{z})_i = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}} \quad \text{where } \sum_{i=1}^{K} \sigma(\mathbf{z})_i = 1$$
This allows the system to display prediction confidence percentages and rank top-3 candidates.

---

## 4. Full-Stack & Backend Architecture

### Q9: How does user authentication and session management work in this application?
**Answer:** The system uses Flask's secure signed session cookies. When a user registers or logs in with verified credentials, Flask stores the authenticated `user_id` inside an encrypted, tamper-proof session cookie signed by `SECRET_KEY`. Protected endpoints enforce authentication via a custom `@login_required` decorator, ensuring unauthenticated visitors are redirected to `/login` and users can only view their own prediction records.

### Q10: How are user passwords secured?
**Answer:** Passwords are never stored in plain text. We use Werkzeug's `generate_password_hash()`, which applies a unique cryptographic salt and the PBKDF2-HMAC-SHA256 algorithm to hash passwords before storing them in the database.

### Q11: How do you prevent SQL Injection attacks?
**Answer:** All database operations in `database/db.py` use parameterized SQL queries (e.g. `cursor.execute("SELECT * FROM users WHERE email = %s", (email,))`). Values are treated strictly as data literals rather than executable SQL code, preventing SQL injection vulnerabilities.

---

## 5. Database & Storage Architecture

### Q12: Explain the database schema design and SQLite fallback.
**Answer:** The database schema (`database/schema.sql`) contains 5 relational tables:
- `users`: Stores user identity, name, email, and hashed credentials.
- `disease_predictions`: Stores uploaded leaf image filenames, diagnosed crop, disease name, confidence score, and foreign key `user_id`.
- `disease_recommendations`: Stores structured symptoms, cultural prevention, and chemical fungicide guidelines for each diagnosis.
- `crop_recommendations`: Stores $N, P, K$, climate inputs, recommended crop, confidence, and foreign key `user_id`.
- `crop_information`: Stores complete agronomic reference guides for all 22 supported crops.
The application supports standard MySQL Server / MariaDB with an automated SQLite fallback (`database/smart_crop.db`), ensuring 100% reliable execution during college demonstrations.

### Q13: How does the Leaf Photo Upload process work?
**Answer:** Farmers access `/predict` and drag-and-drop or select a leaf photo. A client-side JavaScript handler validates image format and size, then previews the photo instantly. On submission, the file is transmitted via `multipart/form-data` to Flask, where PIL verifies file integrity, resizes it to $224 \times 224 \times 3$, runs MobileNetV2 inference, checks the 60% confidence threshold, queries agronomic remedies, and saves the transaction to the database.
