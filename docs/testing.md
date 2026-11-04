# Comprehensive Testing & Quality Assurance Report

## 1. Automated Test Suites

The project includes two primary automated test suites:
1. **Application & Integration Tests (`test_app.py`)**: Executes 9 unit/integration test cases using Python's `unittest` framework and Flask test client, covering authentication, session protection, user data isolation, file upload validation, disease inference, and soil analysis.
2. **Machine Learning Model Tests (`ml/test_models.py`)**: Directly validates loading, vector scaling, class outputs, and prediction accuracy for both the Random Forest crop recommender (22 crops) and the MobileNetV2 CNN disease classifier (16 classes).
3. **Sample Inference Verification (`prepare_samples.py` & `predict_sample.py`)**: Validates 14 test leaf images (2 per each of the 7 supported crops) achieving 99.6%–100.0% confidence.

---

## 2. Test Execution Matrix

| Test ID | Module | Test Function | Verified Behavior | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Database | `test_database_knowledge_base_profiles` | Confirms all 16 model classes exist with full symptoms & cures | **PASSED** |
| **TC-02** | Auth | `test_user_registration_and_login` | Tests new user registration, session creation, and password verification | **PASSED** |
| **TC-03** | Auth | `test_login_invalid_credentials` | Verifies rejection of incorrect passwords with user warning | **PASSED** |
| **TC-04** | Security | `test_unauthenticated_access_redirection` | Verifies `@login_required` redirects guests to `/login` | **PASSED** |
| **TC-05** | Disease ML | `test_file_upload_prediction_flow` | Multipart image upload → MobileNetV2 inference → 200 OK result | **PASSED** |
| **TC-06** | Validation | `test_file_upload_empty_validation` | Submitting `/predict` without an image flashes an upload warning | **PASSED** |
| **TC-07** | Crop ML | `test_crop_recommendation_flow` | Soil parameters → Random Forest prediction → 200 OK result | **PASSED** |
| **TC-08** | Isolation | `test_user_isolation_crop_history` | Verifies User A cannot see User B's historical records | **PASSED** |
| **TC-09** | Validation | `test_crop_recommendation_invalid_input` | Rejects out-of-bounds soil nutrient values | **PASSED** |

---

## 3. How to Run Automated Tests

Execute all tests from the project root in terminal / PowerShell:

```powershell
# 1. Run Complete Web Application & Database Test Suite (9 Tests)
python test_app.py

# 2. Run Both Machine Learning Model Verifications
python ml/test_models.py

# 3. Run Inference on All 14 Desktop Sample Leaf Images
python prepare_samples.py
```
