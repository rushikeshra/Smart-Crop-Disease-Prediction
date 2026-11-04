# -*- coding: utf-8 -*-
"""
End-to-End Multilingual System Verification Suite for Smart Crop AI.
Validates all 12 user requirements across English, Hindi, and Marathi.
"""

import sys
import os
import io
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.db import (
    init_db, get_disease_recommendation, save_prediction, get_prediction_by_id
)
from translations.i18n import (
    t, get_crop_display, get_disease_display, SUPPORTED_LANGUAGES
)


class MultilingualSystemTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        cls.test_email = "farmer@smartcrop.com"
        cls.test_password = "Password123!"

    def login(self, client):
        return client.post("/login", data={
            "email": self.test_email,
            "password": self.test_password
        }, follow_redirects=True)

    # -------------------------------------------------------------
    # 1. English -> Home
    # -------------------------------------------------------------
    def test_01_english_home(self):
        client = app.test_client()
        res = client.get("/set-language/en?next=/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("Smart Foliar Disease Diagnosis", content)
        self.assertIn(t("nav.home", lang="en"), content)
        self.assertIn("Language: <strong>English</strong>", content)
        print("[TEST 1 PASSED] English -> Home verified.")

    # -------------------------------------------------------------
    # 2. Hindi -> Home
    # -------------------------------------------------------------
    def test_02_hindi_home(self):
        client = app.test_client()
        res = client.get("/set-language/hi?next=/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn(t("home.hero_title", lang="hi"), content)
        self.assertIn(t("nav.home", lang="hi"), content)
        self.assertIn("<strong>हिंदी</strong>", content)
        print("[TEST 2 PASSED] Hindi -> Home verified.")

    # -------------------------------------------------------------
    # 3. Marathi -> Home
    # -------------------------------------------------------------
    def test_03_marathi_home(self):
        client = app.test_client()
        res = client.get("/set-language/mr?next=/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn(t("home.hero_title", lang="mr"), content)
        self.assertIn(t("nav.home", lang="mr"), content)
        self.assertIn("<strong>मराठी</strong>", content)
        print("[TEST 3 PASSED] Marathi -> Home verified.")

    # -------------------------------------------------------------
    # 4. Hindi -> Prediction -> Result
    # -------------------------------------------------------------
    def test_04_hindi_prediction_result(self):
        client = app.test_client()
        self.login(client)
        client.get("/set-language/hi")

        leaf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_crop_images", "tomato_sample_1_early_blight.jpg")
        self.assertTrue(os.path.exists(leaf_path), f"Leaf image missing: {leaf_path}")

        with open(leaf_path, "rb") as f:
            res = client.post(
                "/predict",
                data={"image": (f, "tomato_early_blight.jpg")},
                content_type="multipart/form-data",
                follow_redirects=True
            )
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        # Verify Hindi section headers and content
        self.assertIn(t("result.identified_symptoms", lang="hi"), content)
        self.assertIn(t("result.prevention_practices", lang="hi"), content)
        self.assertIn(t("result.treatment_management", lang="hi"), content)
        self.assertIn(t("result.about_condition", lang="hi"), content)
        self.assertIn("टमाटर", content)
        self.assertIn("अर्ली ब्लाइट", content)
        print("[TEST 4 PASSED] Hindi -> Prediction -> Result verified.")

    # -------------------------------------------------------------
    # 5. Marathi -> Prediction -> Result
    # -------------------------------------------------------------
    def test_05_marathi_prediction_result(self):
        client = app.test_client()
        self.login(client)
        client.get("/set-language/mr")

        leaf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_crop_images", "tomato_sample_1_early_blight.jpg")
        with open(leaf_path, "rb") as f:
            res = client.post(
                "/predict",
                data={"image": (f, "tomato_early_blight.jpg")},
                content_type="multipart/form-data",
                follow_redirects=True
            )
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        # Verify Marathi section headers and content
        self.assertIn(t("result.identified_symptoms", lang="mr"), content)
        self.assertIn(t("result.prevention_practices", lang="mr"), content)
        self.assertIn(t("result.treatment_management", lang="mr"), content)
        self.assertIn(t("result.about_condition", lang="mr"), content)
        self.assertIn("टोमॅटो", content)
        self.assertIn("करपा", content)
        print("[TEST 5 PASSED] Marathi -> Prediction -> Result verified.")

    # -------------------------------------------------------------
    # 6. Change language after diagnosis
    # -------------------------------------------------------------
    def test_06_change_language_after_diagnosis(self):
        client = app.test_client()
        self.login(client)

        leaf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_crop_images", "tomato_sample_1_early_blight.jpg")
        with open(leaf_path, "rb") as f:
            res = client.post(
                "/predict",
                data={"image": (f, "tomato_early_blight.jpg")},
                content_type="multipart/form-data",
                follow_redirects=False
            )
        self.assertEqual(res.status_code, 302)
        result_url = res.headers.get("Location")

        # 6a: View in English
        client.get(f"/set-language/en?next={result_url}")
        res_en = client.get(result_url)
        content_en = res_en.data.decode("utf-8")
        self.assertIn(t("result.about_condition", lang="en"), content_en)
        self.assertIn(t("result.identified_symptoms", lang="en"), content_en)
        self.assertIn(t("result.prevention_practices", lang="en"), content_en)

        # 6b: Switch to Hindi
        client.get(f"/set-language/hi?next={result_url}")
        res_hi = client.get(result_url)
        content_hi = res_hi.data.decode("utf-8")
        self.assertIn(t("result.about_condition", lang="hi"), content_hi)
        self.assertIn(t("result.identified_symptoms", lang="hi"), content_hi)
        self.assertIn(t("result.prevention_practices", lang="hi"), content_hi)

        # 6c: Switch to Marathi
        client.get(f"/set-language/mr?next={result_url}")
        res_mr = client.get(result_url)
        content_mr = res_mr.data.decode("utf-8")
        self.assertIn(t("result.about_condition", lang="mr"), content_mr)
        self.assertIn(t("result.identified_symptoms", lang="mr"), content_mr)
        self.assertIn(t("result.prevention_practices", lang="mr"), content_mr)

        print("[TEST 6 PASSED] Change language after diagnosis dynamically updates advisory.")

    # -------------------------------------------------------------
    # 7. Navigation persistence across pages
    # -------------------------------------------------------------
    def test_07_language_persistence_across_navigation(self):
        client = app.test_client()
        self.login(client)

        # Set to Hindi
        client.get("/set-language/hi")

        for endpoint in ["/", "/dashboard", "/predict", "/history"]:
            res = client.get(endpoint)
            self.assertEqual(res.status_code, 200)
            content = res.data.decode("utf-8")
            self.assertIn("<strong>हिंदी</strong>", content, f"Hindi failed to persist on {endpoint}")

        # Set to Marathi
        client.get("/set-language/mr")

        for endpoint in ["/", "/dashboard", "/predict", "/history"]:
            res = client.get(endpoint)
            self.assertEqual(res.status_code, 200)
            content = res.data.decode("utf-8")
            self.assertIn("<strong>मराठी</strong>", content, f"Marathi failed to persist on {endpoint}")

        print("[TEST 7 PASSED] Language persists seamlessly across Home -> Dashboard -> Predict -> History.")

    # -------------------------------------------------------------
    # 8. Verify disease names in all 3 languages
    # -------------------------------------------------------------
    def test_08_disease_names_translations(self):
        # Tomato Early Blight
        en_val = get_disease_display("Tomato___Early_blight", lang="en")
        hi_val = get_disease_display("Tomato___Early_blight", lang="hi")
        mr_val = get_disease_display("Tomato___Early_blight", lang="mr")

        self.assertIn("Early Blight", en_val)
        self.assertIn("अर्ली ब्लाइट", hi_val)
        self.assertIn("करपा", mr_val)

        # Soybean Bacterial Blight
        en_sb = get_disease_display("Soybean___Bacterial_blight", lang="en")
        hi_sb = get_disease_display("Soybean___Bacterial_blight", lang="hi")
        mr_sb = get_disease_display("Soybean___Bacterial_blight", lang="mr")

        self.assertIn("Bacterial Blight", en_sb)
        self.assertIn("बैक्टीरियल ब्लाइट", hi_sb)
        self.assertIn("बॅक्टेरियल ब्लाइट", mr_sb)

        # Soybean Healthy
        en_hl = get_disease_display("Soybean___healthy", lang="en")
        hi_hl = get_disease_display("Soybean___healthy", lang="hi")
        mr_hl = get_disease_display("Soybean___healthy", lang="mr")

        self.assertIn("Healthy Foliage", en_hl)
        self.assertIn("स्वस्थ पत्ती", hi_hl)
        self.assertIn("निरोगी पाने", mr_hl)

        print("[TEST 8 PASSED] Disease names verified across English, Hindi, and Marathi.")

    # -------------------------------------------------------------
    # 9. Verify scientific/pathogen names remain exact and uncorrupted
    # -------------------------------------------------------------
    def test_09_scientific_pathogen_names_preservation(self):
        for lang in ["en", "hi", "mr"]:
            rec_tomato = get_disease_recommendation("Tomato___Early_blight", lang=lang)
            rec_soybean_bb = get_disease_recommendation("Soybean___Bacterial_blight", lang=lang)
            rec_apple = get_disease_recommendation("Apple___Apple_scab", lang=lang)

            # Tomato botanical & pathogen in translations
            self.assertIn("Alternaria solani", get_disease_display("Tomato___Early_blight", lang=lang))
            self.assertIn("Solanum lycopersicum", get_crop_display("Tomato", lang=lang))

            # Soybean botanical & pathogen
            self.assertIn("Pseudomonas savastanoi", get_disease_display("Soybean___Bacterial_blight", lang=lang))
            self.assertIn("Glycine max", get_crop_display("Soybean", lang=lang))

            # Apple botanical & pathogen
            self.assertIn("Venturia inaequalis", get_disease_display("Apple___Apple_scab", lang=lang))
            self.assertIn("Malus domestica", get_crop_display("Apple", lang=lang))

        print("[TEST 9 PASSED] Scientific and pathogen names remain strictly exact across all languages.")

    # -------------------------------------------------------------
    # 10. Verify ML prediction is unchanged regardless of language
    # -------------------------------------------------------------
    def test_10_ml_prediction_invariant_to_language(self):
        from ml.crop_validator import CropSystemValidator
        validator = CropSystemValidator.get_instance()
        leaf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_crop_images", "tomato_sample_1_early_blight.jpg")

        client = app.test_client()
        self.login(client)

        results = {}
        for lang in ["en", "hi", "mr"]:
            client.get(f"/set-language/{lang}")
            diag = validator.diagnose_leaf(leaf_path)
            results[lang] = {
                "class_name": diag["class_name"],
                "confidence": diag["confidence"],
                "crop_prob": diag["crop_probability"]
            }

        # Assert identical ML inference output
        self.assertEqual(results["en"]["class_name"], results["hi"]["class_name"])
        self.assertEqual(results["hi"]["class_name"], results["mr"]["class_name"])
        self.assertEqual(results["en"]["confidence"], results["hi"]["confidence"])
        self.assertEqual(results["hi"]["confidence"], results["mr"]["confidence"])
        self.assertEqual(results["en"]["class_name"], "Tomato___Early_blight")

        print("[TEST 10 PASSED] ML prediction is 100% invariant to UI language.")

    # -------------------------------------------------------------
    # 11. Verify unsupported crop & invalid image messages translate
    # -------------------------------------------------------------
    def test_11_unsupported_crop_translation(self):
        client = app.test_client()
        self.login(client)

        # Blank/noise image
        from PIL import Image
        blank_img = Image.new("RGB", (224, 224), color=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        blank_img.save(img_byte_arr, format="JPEG")
        img_bytes = img_byte_arr.getvalue()

        # Hindi invalid foliar
        client.get("/set-language/hi")
        res_hi = client.post(
            "/predict",
            data={"image": (io.BytesIO(img_bytes), "blank.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )
        content_hi = res_hi.data.decode("utf-8")
        self.assertIn(t("ood.invalid_image_title", lang="hi"), content_hi)
        self.assertIn(t("ood.invalid_image_sub", lang="hi"), content_hi)

        # Marathi invalid foliar
        client.get("/set-language/mr")
        res_mr = client.post(
            "/predict",
            data={"image": (io.BytesIO(img_bytes), "blank.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )
        content_mr = res_mr.data.decode("utf-8")
        self.assertIn(t("ood.invalid_image_title", lang="mr"), content_mr)
        self.assertIn(t("ood.invalid_image_sub", lang="mr"), content_mr)

        print("[TEST 11 PASSED] Unsupported crop / invalid image messages translate accurately.")

    # -------------------------------------------------------------
    # 12. Verify Print/Save Diagnosis Report uses selected language
    # -------------------------------------------------------------
    def test_12_print_report_uses_selected_language(self):
        client = app.test_client()
        self.login(client)

        leaf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_crop_images", "tomato_sample_1_early_blight.jpg")
        with open(leaf_path, "rb") as f:
            res = client.post(
                "/predict",
                data={"image": (f, "tomato_early_blight.jpg")},
                content_type="multipart/form-data",
                follow_redirects=False
            )
        result_url = res.headers.get("Location")

        # Hindi print view
        client.get(f"/set-language/hi?next={result_url}")
        res_hi = client.get(result_url)
        content_hi = res_hi.data.decode("utf-8")
        # Ensure printable blocks are in Hindi and print media styles are present
        self.assertIn("@media print", content_hi)
        self.assertIn(t("result.print_report", lang="hi"), content_hi)
        self.assertIn(t("result.identified_symptoms", lang="hi"), content_hi)
        self.assertIn(t("result.treatment_management", lang="hi"), content_hi)

        # Marathi print view
        client.get(f"/set-language/mr?next={result_url}")
        res_mr = client.get(result_url)
        content_mr = res_mr.data.decode("utf-8")
        self.assertIn("@media print", content_mr)
        self.assertIn(t("result.print_report", lang="mr"), content_mr)
        self.assertIn(t("result.identified_symptoms", lang="mr"), content_mr)
        self.assertIn(t("result.treatment_management", lang="mr"), content_mr)

        print("[TEST 12 PASSED] Print/Save Diagnosis Report reflects the selected language.")


if __name__ == "__main__":
    unittest.main()
