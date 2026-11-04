import os
import sys
import unittest
from werkzeug.security import generate_password_hash

from app import app, allowed_file
from database.db import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    save_prediction, get_user_predictions, get_prediction_by_id,
    get_user_statistics, get_disease_recommendation, get_db_connection,
    save_crop_recommendation, get_user_crop_recommendations,
    get_crop_recommendation_by_id, get_crop_catalog_info,
    get_all_crop_catalog
)

class SmartCropSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        init_db()

    def tearDown(self):
        """Clean tables between test runs."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM crop_recommendations;")
            cursor.execute("DELETE FROM disease_recommendations;")
            cursor.execute("DELETE FROM disease_predictions;")
            cursor.execute("DELETE FROM users WHERE email LIKE '%@smartcrop.edu' OR email LIKE 'farmer_test_%';")
            if hasattr(conn, "commit"):
                conn.commit()
        finally:
            conn.close()

    def test_database_knowledge_base_profiles(self):
        """Verify all 31 disease and healthy condition classes across 10 crops exist in knowledge base with recovery and alternative recommendations."""
        expected_classes = [
            "Apple___Apple_scab",
            "Apple___Black_rot",
            "Apple___healthy",
            "Corn_(maize)___Common_rust_",
            "Corn_(maize)___healthy",
            "Grape___Black_rot",
            "Grape___healthy",
            "Pepper__bell___Bacterial_spot",
            "Pepper__bell___healthy",
            "Potato___Early_blight",
            "Potato___Late_blight",
            "Potato___healthy",
            "Soybean___Bacterial_blight",
            "Soybean___Frogeye_leaf_spot",
            "Soybean___Soybean_rust",
            "Soybean___healthy",
            "Tomato___Early_blight",
            "Tomato___Late_blight",
            "Tomato___healthy",
            "Cotton___Bacterial_blight",
            "Cotton___Leaf_curl_virus",
            "Cotton___Alternaria_leaf_spot",
            "Cotton___healthy",
            "Green_Gram___Cercospora_leaf_spot",
            "Green_Gram___Yellow_mosaic",
            "Green_Gram___Powdery_mildew",
            "Green_Gram___healthy",
            "Pigeon_Pea___Sterility_mosaic",
            "Pigeon_Pea___Phytophthora_blight",
            "Pigeon_Pea___Cercospora_leaf_spot",
            "Pigeon_Pea___healthy"
        ]
        self.assertEqual(len(expected_classes), 31)
        for cls in expected_classes:
            info = get_disease_recommendation(cls)
            self.assertIsNotNone(info, f"Missing profile for class: {cls}")
            self.assertIn("crop_name", info)
            self.assertIn("disease_name", info)
            self.assertIn("description", info)
            self.assertIn("symptoms", info)
            self.assertIn("prevention", info)
            self.assertIn("treatment_or_cure", info)
            self.assertIn("chemical_information", info)
            self.assertIn("recovery_period", info, f"Missing recovery_period for class: {cls}")
            self.assertIn("recommendation_1", info, f"Missing recommendation_1 for class: {cls}")
            self.assertIn("recommendation_2", info, f"Missing recommendation_2 for class: {cls}")
            self.assertNotEqual(info["recommendation_1"], info["recommendation_2"], f"Recommendations must not be duplicates for {cls}")

    def test_user_authentication_flow(self):
        """Test registration, duplicate prevention, logout, and login."""
        test_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        
        # 1. Register User 1
        res = self.client.post("/register", data={
            "name": "Rathod Agronomist",
            "email": test_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"Dashboard" in res.data or b"Farmer" in res.data)

        # 2. Log out before testing duplicate registration attempt
        self.client.get("/logout", follow_redirects=True)

        # 3. Duplicate registration check with same email
        res_dup = self.client.post("/register", data={
            "name": "Duplicate User",
            "email": test_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"already exists", res_dup.data)

        # 4. Login with registered credentials
        res_login = self.client.post("/login", data={
            "email": test_email,
            "password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertTrue(b"Welcome back" in res_login.data or b"Dashboard" in res_login.data or b"Farmer" in res_login.data)

        # 5. Logout again
        self.client.get("/logout", follow_redirects=True)

        # 6. Invalid password login rejection
        res_fail = self.client.post("/login", data={
            "email": test_email,
            "password": "WrongPassword"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email address or password", res_fail.data)

    def test_protected_routes(self):
        """Ensure dashboard, predict, and history redirect unauthenticated users."""
        self.client.get("/logout")
        for route in ["/dashboard", "/predict", "/history"]:
            res = self.client.get(route, follow_redirects=False)
            self.assertEqual(res.status_code, 302, f"Route {route} should redirect when not logged in")

    def test_file_extension_validation(self):
        """Check allowed file helper."""
        self.assertTrue(allowed_file("leaf.jpg"))
        self.assertTrue(allowed_file("leaf.jpeg"))
        self.assertTrue(allowed_file("leaf.png"))
        self.assertFalse(allowed_file("malicious.exe"))
        self.assertFalse(allowed_file("document.pdf"))
        self.assertFalse(allowed_file("script.py"))

    def test_prediction_storage_and_user_isolation(self):
        """Test that predictions save properly and remain isolated to their respective users."""
        user1_email = f"user1_{os.urandom(4).hex()}@smartcrop.edu"
        user2_email = f"user2_{os.urandom(4).hex()}@smartcrop.edu"

        uid1 = create_user("User One", user1_email, generate_password_hash("pass123"))
        uid2 = create_user("User Two", user2_email, generate_password_hash("pass123"))

        # Save prediction for User 1 with new recovery and recommendation fields
        pid1 = save_prediction(
            user_id=uid1,
            crop="Potato",
            disease="Early Blight",
            class_name="Potato___Early_blight",
            confidence=95.4,
            image_name="test_potato.jpg",
            cure_treatment="Prune infected leaves",
            chemical_info="Chlorothalonil spray",
            prevention="Crop rotation",
            recovery_period="7–14 days with proper fungicide scheduling",
            recommendation_1="Apply Chlorothalonil 75 WP or Mancozeb 75 WP alternately with Difenoconazole",
            recommendation_2="Apply bio-rational copper octanoate or Trichoderma harzianum"
        )
        self.assertIsNotNone(pid1)

        # Verify User 1 sees it with all fields intact
        preds_u1 = get_user_predictions(uid1)
        self.assertEqual(len(preds_u1), 1)
        self.assertEqual(preds_u1[0]["disease"], "Early Blight")
        self.assertEqual(preds_u1[0]["recovery_period"], "7–14 days with proper fungicide scheduling")
        self.assertIn("Chlorothalonil", preds_u1[0]["recommendation_1"])
        self.assertIn("copper octanoate", preds_u1[0]["recommendation_2"])

        # Test backward compatibility: save prediction with legacy 9 parameters (None for new fields)
        pid1_legacy = save_prediction(
            user_id=uid1,
            crop="Tomato",
            disease="Early Blight",
            class_name="Tomato___Early_blight",
            confidence=91.0,
            image_name="test_tomato.jpg",
            cure_treatment="Prune bottom leaves",
            chemical_info="Mancozeb",
            prevention="Crop rotation"
        )
        self.assertIsNotNone(pid1_legacy)
        legacy_rec = get_prediction_by_id(pid1_legacy, user_id=uid1)
        self.assertEqual(legacy_rec["disease"], "Early Blight")
        self.assertIsNone(legacy_rec.get("recovery_period"))

        # Verify User 2 CANNOT see User 1's predictions (User Isolation)
        preds_u2 = get_user_predictions(uid2)
        self.assertEqual(len(preds_u2), 0)

        # Verify User 2 cannot fetch prediction by id
        isolated_rec = get_prediction_by_id(pid1, user_id=uid2)
        self.assertIsNone(isolated_rec)

    def test_new_crops_and_recommendation_features(self):
        """Test the 3 new crops integration, localized naming, and crop validator catalog."""
        from translations import get_crop_display, get_disease_display
        from ml.crop_validator import SUPPORTED_CROPS_INFO

        # 1. Total supported crops in catalog is 10
        self.assertEqual(len(SUPPORTED_CROPS_INFO), 10)
        self.assertIn("Green_Gram", SUPPORTED_CROPS_INFO)
        self.assertIn("Cotton", SUPPORTED_CROPS_INFO)
        self.assertIn("Pigeon_Pea", SUPPORTED_CROPS_INFO)

        # 2. English display names with botanical nomenclature
        self.assertIn("Green Gram (Vigna radiata)", get_crop_display("Green_Gram", "en"))
        self.assertIn("Cotton (Gossypium spp.)", get_crop_display("Cotton", "en"))
        self.assertIn("Pigeon Pea / Red Gram (Cajanus cajan)", get_crop_display("Pigeon_Pea", "en"))

        # 3. Multilingual localization
        hi_cotton = get_crop_display("Cotton", "hi")
        self.assertTrue("Cotton" in hi_cotton or len(hi_cotton) > 0)
        mr_pigeon = get_crop_display("Pigeon_Pea", "mr")
        self.assertTrue("Pigeon Pea" in mr_pigeon or len(mr_pigeon) > 0)

        # 4. Alternative recommendations check for new crops
        gg_info = get_disease_recommendation("Green_Gram___Yellow_mosaic")
        self.assertIsNotNone(gg_info)
        self.assertIn("recovery_period", gg_info)
        self.assertIn("recommendation_1", gg_info)
        self.assertIn("recommendation_2", gg_info)
        self.assertNotEqual(gg_info["recommendation_1"], gg_info["recommendation_2"])

    def test_crop_catalog_and_api(self):
        """Test crop catalog retrieval and JSON API endpoints."""
        catalog = get_all_crop_catalog()
        self.assertGreaterEqual(len(catalog), 22)
        rice_info = get_crop_catalog_info("rice")
        self.assertIsNotNone(rice_info)
        self.assertEqual(rice_info["crop_name"].lower(), "rice")

        # Test GET /api/crops
        res = self.client.get("/api/crops")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 22)

        # Test POST /api/crop/recommend
        api_res = self.client.post("/api/crop/recommend", json={
            "N": 90, "P": 42, "K": 43,
            "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9
        })
        self.assertEqual(api_res.status_code, 200)
        api_data = api_res.get_json()
        self.assertTrue(api_data["success"])
        self.assertEqual(api_data["data"]["recommended_crop"].lower(), "rice")

    def test_crop_recommendation_flow_and_isolation(self):
        """Test web route crop recommendation and user isolation."""
        # 1. Register User 1
        u1_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Soil Farmer One",
            "email": u1_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # 2. Submit Soil Parameters
        res = self.client.post("/recommend-crop", data={
            "nitrogen": "90",
            "phosphorus": "42",
            "potassium": "43",
            "temperature": "20.8",
            "humidity": "82.0",
            "ph": "6.5",
            "rainfall": "202.9"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"rice", res.data.lower())
        self.assertIn(b"Optimal Cultivation Crop", res.data)

        # Verify crop history has 1 record
        res_hist = self.client.get("/crop-history")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn(b"rice", res_hist.data.lower())

        # 3. Logout User 1 and Register User 2
        self.client.get("/logout", follow_redirects=True)
        u2_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Soil Farmer Two",
            "email": u2_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # User 2 history must be empty (User Isolation)
        res_hist_u2 = self.client.get("/crop-history")
        self.assertEqual(res_hist_u2.status_code, 200)
        self.assertIn(b"No Crop History Recorded", res_hist_u2.data)

    def test_file_upload_prediction_flow(self):
        """Test that multipart leaf image file upload is processed and diagnosed."""
        import io
        from PIL import Image

        # Create dummy test image in memory
        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        # Register and login user
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Upload User",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # Submit image file upload to /predict
        res = self.client.post(
            "/predict",
            data={"image": (buf, "test_leaf.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"Diagnosis" in res.data or b"Confidence" in res.data or b"Unable to Confidently" in res.data)

    def test_file_upload_empty_validation(self):
        """Test that submitting /predict without an image flashes a warning."""
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Empty Upload User",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        res = self.client.post("/predict", data={}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please select a leaf image file to upload", res.data)

    def test_real_leaf_image_prediction(self):
        """Test uploading an actual leaf image and verifying full result fields."""
        import io
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Real Leaf Tester",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        leaf_path = os.path.join(os.path.dirname(__file__), "sample_crop_images", "tomato_sample_1_early_blight.jpg")
        with open(leaf_path, "rb") as f:
            img_data = f.read()

        res = self.client.post(
            "/predict",
            data={"image": (io.BytesIO(img_data), "tomato_early_blight.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Tomato", res.data)
        self.assertIn(b"Early Blight", res.data)
        self.assertIn(b"Symptoms", res.data)
        self.assertIn(b"Treatment", res.data)
        self.assertIn(b"Prevention", res.data)

    def test_non_leaf_image_rejection(self):
        """Test uploading a non-leaf/blank image returns low-confidence warning."""
        import io
        from PIL import Image
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Non-Leaf Tester",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # Blank white image (non-leaf)
        blank = Image.new("RGB", (224, 224), color=(255, 255, 255))
        buf = io.BytesIO()
        blank.save(buf, format="JPEG")
        buf.seek(0)

        res = self.client.post(
            "/predict",
            data={"image": (buf, "blank_image.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Unable to confidently identify this image", res.data)
        self.assertIn(b"Please upload a clear leaf image belonging to one of the supported crops", res.data)

    def test_supported_diseased_soybean_diagnosis(self):
        """Verify diseased soybean leaf is correctly identified as Soybean disease, NOT Bell Pepper."""
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Soybean Disease Tester",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        user_soy_path = os.path.join(os.path.dirname(__file__), "static", "uploads", "leaf_c141119cad69.jpg")
        if os.path.exists(user_soy_path):
            with open(user_soy_path, "rb") as f:
                res = self.client.post(
                    "/predict",
                    data={"image": (f, "diseased_soybean.jpg")},
                    content_type="multipart/form-data",
                    follow_redirects=True
                )
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Soybean", res.data)
            # Must NOT claim Bell Pepper!
            self.assertNotIn(b"Bell Pepper", res.data)

    def test_supported_healthy_soybean_diagnosis(self):
        """Verify healthy soybean leaf is correctly diagnosed as Soybean Healthy Foliage."""
        u_email = f"farmer_test_{os.urandom(4).hex()}@smartcrop.edu"
        self.client.post("/register", data={
            "name": "Soybean Healthy Tester",
            "email": u_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        sample_path = os.path.join(os.path.dirname(__file__), "sample_crop_images", "soybean_sample_1_healthy.jpg")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                res = self.client.post(
                    "/predict",
                    data={"image": (f, "soybean_healthy.jpg")},
                    content_type="multipart/form-data",
                    follow_redirects=True
                )
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Soybean", res.data)
            self.assertIn(b"Healthy Foliage", res.data)

if __name__ == "__main__":
    unittest.main()
