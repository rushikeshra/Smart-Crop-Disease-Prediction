import os
import sys
import subprocess

# Auto-forward to project's virtual environment if executed via system python
_PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_PROJ_DIR)

_CANDIDATE_VENV_PYTHONS = [
    os.path.join(_PROJ_DIR, ".venv", "Scripts", "python.exe"),
    os.path.join(os.path.dirname(_PROJ_DIR), "My_Project", ".venv", "Scripts", "python.exe"),
    os.path.join(os.path.dirname(_PROJ_DIR), "My-Project", ".venv", "Scripts", "python.exe"),
    r"C:\Users\ASUS\OneDrive\Desktop\My_Project\.venv\Scripts\python.exe",
    r"C:\Users\ASUS\OneDrive\Desktop\My-Project\.venv\Scripts\python.exe"
]

_target_python = None
for _p in _CANDIDATE_VENV_PYTHONS:
    if os.path.exists(_p):
        _target_python = os.path.abspath(_p)
        break

if _target_python:
    _curr = os.path.abspath(sys.executable).lower()
    if _curr != _target_python.lower():
        sys.exit(subprocess.call([_target_python] + sys.argv, cwd=_PROJ_DIR))

import uuid
import json
import re
import base64
import numpy as np
from functools import wraps
from PIL import Image

from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database.db import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    save_prediction, get_user_predictions, get_prediction_by_id,
    get_user_statistics, get_disease_recommendation,
    save_crop_recommendation, get_user_crop_recommendations,
    get_crop_recommendation_by_id, get_crop_catalog_info,
    get_all_crop_catalog
)
from translations import (
    t, get_current_language, set_current_language,
    get_crop_display, get_disease_display, SUPPORTED_LANGUAGES
)

try:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[WARNING] TensorFlow not found. Model inference will be disabled.")

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

_MODEL = None
_CLASS_NAMES = None

def parse_class_name(class_name):
    """Cleanly parse class names into human-readable Crop and Disease labels."""
    if "___" in class_name:
        parts = class_name.split("___", 1)
        raw_crop, raw_disease = parts[0], parts[1]
    else:
        parts = class_name.split("_", 1)
        raw_crop = parts[0]
        raw_disease = parts[1] if len(parts) > 1 else "Unknown"

    crop = raw_crop.replace("(maize)", "(Corn)").replace("__bell", " (Bell)").replace("_", " ").strip()
    disease = raw_disease.replace("_", " ").strip()
    if disease.lower() == "healthy":
        disease = "Healthy Foliage"
    return crop, disease

def is_likely_foliar_image(image_path):
    """
    Quality & domain verification: checks whether an uploaded image contains
    sufficient foliar/vegetation colors (green, chlorotic yellow, or necrotic brown)
    and has adequate image detail (non-blank).
    """
    try:
        with Image.open(image_path) as img:
            img_rgb = img.convert("RGB").resize((128, 128))
            arr = np.array(img_rgb, dtype=np.float32)

            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            std_dev = float(np.std(arr))

            # Reject blank or solid color pictures (low contrast)
            if std_dev < 14.0:
                return False, "Image appears blank or lacks visual variation."

            # Leaf pixel masks:
            # 1. Healthy green foliage
            green_mask = (g > r * 1.05) & (g > b * 1.05) & (g > 35)
            # 2. Chlorotic or yellowish leaf tissue
            yellow_mask = (r > 65) & (g > 65) & (r > b * 1.2) & (g > b * 1.2)
            # 3. Necrotic / blight / leaf spot brown tissue
            brown_mask = (r > 40) & (g > 25) & (r > g * 1.05) & (g > b * 1.05) & (r < 210) & (b < 110)

            foliar_coverage = float(np.mean(green_mask | yellow_mask | brown_mask))

            # If image has under 7% plant/leaf coloration, flag as non-leaf
            if foliar_coverage < 0.07:
                return False, "Image does not have sufficient foliar or plant leaf characteristics."

            return True, None
    except Exception as e:
        # If inspection encounters an issue, proceed to model prediction
        return True, None

def load_ml_model():
    """Load trained MobileNetV2 model and class mapping safely for inference."""
    global _MODEL, _CLASS_NAMES
    if not TF_AVAILABLE:
        print("[ML ERROR] TensorFlow is not available in environment.")
        return None, None

    model_path = app.config["MODEL_PATH"]
    mapping_path = app.config["CLASS_NAMES_PATH"]

    if _MODEL is None:
        candidates = [model_path]
        if ".keras" in model_path:
            candidates.append(model_path.replace(".keras", ".h5"))
        elif ".h5" in model_path:
            candidates.append(model_path.replace(".h5", ".keras"))

        for cpath in candidates:
            if os.path.exists(cpath):
                try:
                    print(f"[ML] Loading disease model from '{os.path.basename(cpath)}'...")
                    _MODEL = tf.keras.models.load_model(cpath, compile=False)
                    print(f"[ML SUCCESS] Disease model loaded from '{os.path.basename(cpath)}'.")
                    break
                except Exception as e:
                    print(f"[ML WARNING] Failed to load disease model from '{os.path.basename(cpath)}': {e}")
                    _MODEL = None
        if _MODEL is None:
            print(f"[ML ERROR] Disease model could not be loaded from candidates: {candidates}")

    if _CLASS_NAMES is None:
        if os.path.exists(mapping_path):
            try:
                with open(mapping_path, "r", encoding="utf-8") as f:
                    mapping = json.load(f)
                if isinstance(mapping, list):
                    _CLASS_NAMES = mapping
                elif isinstance(mapping, dict):
                    _CLASS_NAMES = [mapping[str(i)] if str(i) in mapping else mapping[i] for i in range(len(mapping))]
                else:
                    _CLASS_NAMES = list(mapping)
                print(f"[ML SUCCESS] Loaded {len(_CLASS_NAMES)} class mappings.")
            except Exception as e:
                print(f"[ML ERROR] Failed to load class mapping from '{mapping_path}': {e}")
                import traceback
                traceback.print_exc()
                _CLASS_NAMES = None
        else:
            print(f"[ML ERROR] Class names mapping file not found at: {mapping_path}")

    return _MODEL, _CLASS_NAMES

_CROP_RECOMMENDER = None

def load_crop_recommender():
    """Load CropRecommender model singleton."""
    global _CROP_RECOMMENDER
    if _CROP_RECOMMENDER is None:
        try:
            from ml.crop_recommendation.predict import get_recommender
            _CROP_RECOMMENDER = get_recommender()
            print("[ML SUCCESS] CropRecommender model loaded successfully.")
        except Exception as e:
            print(f"[ML ERROR] Failed to load CropRecommender: {e}")
            _CROP_RECOMMENDER = None
    return _CROP_RECOMMENDER

def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def login_required(f):
    """Decorator to enforce user authentication on routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_template_context():
    """Inject current logged-in user, language state, and translation helpers into all templates."""
    current_user = None
    if "user_id" in session:
        try:
            current_user = get_user_by_id(session["user_id"])
        except Exception:
            current_user = None

    cur_lang = get_current_language()
    return {
        "current_user": current_user,
        "current_language": cur_lang,
        "current_language_name": SUPPORTED_LANGUAGES.get(cur_lang, "English"),
        "supported_languages": SUPPORTED_LANGUAGES,
        "t": t,
        "get_crop_display": get_crop_display,
        "get_disease_display": get_disease_display
    }

@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    """Change the active interface language and redirect back to previous page."""
    if lang_code in SUPPORTED_LANGUAGES:
        session["language"] = lang_code
    next_url = request.args.get("next") or request.referrer or url_for("index")
    if not next_url.startswith("/") or "set-language" in next_url:
        next_url = url_for("index")
    return redirect(next_url)

# ==========================================================
# AUTHENTICATION ROUTES
# ==========================================================

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", name=name, email=email)

        try:
            existing = get_user_by_email(email)
            if existing:
                flash("An account with this email already exists. Please log in.", "warning")
                return redirect(url_for("login"))

            pwd_hash = generate_password_hash(password)
            user_id = create_user(name, email, pwd_hash)
            session["user_id"] = user_id
            session["user_name"] = name
            flash(f"Welcome, {name}! Your account has been registered successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Database error during registration: {e}", "danger")
            return render_template("register.html", name=name, email=email)

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        try:
            user = get_user_by_email(email)
            if not user or not check_password_hash(user["password_hash"], password):
                flash("Invalid email address or password.", "danger")
                return render_template("login.html", email=email)

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("dashboard"))
        except Exception as e:
            flash(f"Error communicating with database: {e}", "danger")
            return render_template("login.html", email=email)

    return render_template("login.html")

@app.route("/logout")
def logout():
    """User logout."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

# ==========================================================
# APPLICATION DASHBOARD & PREDICTION ROUTES
# ==========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard showing summary statistics and recent predictions."""
    user_id = session["user_id"]
    try:
        stats = get_user_statistics(user_id)
        recent_preds = get_user_predictions(user_id, limit=5)
        recent_crops = get_user_crop_recommendations(user_id, limit=3)
        return render_template("dashboard.html", stats=stats, recent_predictions=recent_preds, recent_crops=recent_crops)
    except Exception as e:
        flash(f"Failed to load dashboard data: {e}", "danger")
        return render_template("dashboard.html", stats={}, recent_predictions=[], recent_crops=[])

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    """Leaf disease prediction page (Upload Leaf Photo)."""
    if request.method == "GET":
        return render_template("predict.html")

    user_id = session["user_id"]
    image_saved_path = None
    saved_filename = None

    file = request.files.get("image")
    camera_base64 = request.form.get("camera_base64", "").strip()

    if (not file or file.filename == "") and not camera_base64:
        flash("Please upload an image file or capture a leaf photo using the camera.", "warning")
        return redirect(url_for("predict"))

    try:
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("Unsupported file format. Please upload JPG, JPEG, or PNG images.", "danger")
                return redirect(url_for("predict"))
            ext = file.filename.rsplit(".", 1)[1].lower()
            saved_filename = f"leaf_{uuid.uuid4().hex[:12]}.{ext}"
            image_saved_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)
            file.save(image_saved_path)
        elif camera_base64:
            # Decode camera capture data URL
            if "," in camera_base64:
                _, encoded = camera_base64.split(",", 1)
            else:
                encoded = camera_base64
            img_bytes = base64.b64decode(encoded)
            saved_filename = f"leaf_cam_{uuid.uuid4().hex[:12]}.jpg"
            image_saved_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)
            with open(image_saved_path, "wb") as f_out:
                f_out.write(img_bytes)

        # Verify image integrity with PIL
        with Image.open(image_saved_path) as img:
            img.verify()
    except Exception as e:
        if image_saved_path and os.path.exists(image_saved_path):
            os.remove(image_saved_path)
        flash(f"Invalid or corrupted image: {e}", "danger")
        return redirect(url_for("predict"))

    # Run Two-Stage Crop-Constrained Inference via CropSystemValidator
    try:
        from ml.crop_validator import CropSystemValidator
        validator = CropSystemValidator.get_instance()
        diagnosis = validator.diagnose_leaf(image_saved_path)

        if diagnosis["status"] == "unsupported_crop":
            return render_template(
                "result.html",
                status="unsupported_crop",
                is_low_confidence=False,
                image_name=saved_filename,
                title=diagnosis.get("title", "Unsupported Crop"),
                message=diagnosis.get("message", "This image does not appear to belong to a crop supported by the current model."),
                detected_candidate=diagnosis.get("detected_candidate"),
                supported_crops=diagnosis.get("supported_crops", []),
                confidence=None,
                prediction=None,
                recommendation=None
            )

        elif diagnosis["status"] == "invalid_image":
            return render_template(
                "result.html",
                status="invalid_image",
                is_low_confidence=False,
                image_name=saved_filename,
                title=diagnosis.get("title", "Invalid / Non-Leaf Image"),
                message=diagnosis.get("message", "Uploaded image does not appear to be a plant leaf."),
                supported_crops=diagnosis.get("supported_crops", []),
                confidence=None,
                prediction=None,
                recommendation=None
            )

        elif diagnosis["status"] == "ambiguous_disease":
            return render_template(
                "result.html",
                status="unsupported_crop",
                is_low_confidence=True,
                image_name=saved_filename,
                title=diagnosis.get("title", "Uncertain Soybean Condition"),
                message=diagnosis.get("message", "Soybean detected, but disease could not be reliably identified."),
                detected_candidate=diagnosis.get("crop", "Soybean"),
                supported_crops=diagnosis.get("supported_crops", []),
                confidence=diagnosis.get("confidence"),
                prediction=None,
                recommendation=None
            )

        elif diagnosis["status"] == "success":
            rec_info = diagnosis.get("recommendation", {})
            crop_clean = diagnosis["crop"]
            disease_clean = diagnosis["disease"]
            predicted_class = diagnosis.get("class_name", "")
            confidence = diagnosis.get("confidence", 95.0)

            cure_treatment_text = "\n".join(rec_info.get("treatment_or_cure", [])) if isinstance(rec_info.get("treatment_or_cure"), list) else str(rec_info.get("treatment_or_cure", ""))
            prevention_text = "\n".join(rec_info.get("prevention", [])) if isinstance(rec_info.get("prevention"), list) else str(rec_info.get("prevention", ""))
            chemical_info_text = str(rec_info.get("chemical_information", ""))
            recovery_period_text = str(rec_info.get("recovery_period", ""))
            rec_1_text = str(rec_info.get("recommendation_1", ""))
            rec_2_text = str(rec_info.get("recommendation_2", ""))

            # Save to Database
            pred_id = save_prediction(
                user_id=user_id,
                crop=crop_clean,
                disease=disease_clean,
                class_name=predicted_class,
                confidence=confidence,
                image_name=saved_filename,
                cure_treatment=cure_treatment_text,
                chemical_info=chemical_info_text,
                prevention=prevention_text,
                recovery_period=recovery_period_text,
                recommendation_1=rec_1_text,
                recommendation_2=rec_2_text
            )

            return redirect(url_for("view_result", prediction_id=pred_id))

        else:
            flash(f"Diagnosis unavailable: {diagnosis.get('message', 'Uncertain prediction')}", "warning")
            return redirect(url_for("predict"))

    except Exception as e:
        flash(f"Error occurred during image inference: {e}", "danger")
        return redirect(url_for("predict"))

@app.route("/result/<int:prediction_id>")
@login_required
def view_result(prediction_id):
    """Display full prediction result and agricultural recommendations."""
    user_id = session["user_id"]
    try:
        pred_record = get_prediction_by_id(prediction_id, user_id)
        if not pred_record:
            flash("Prediction record not found or unauthorized.", "warning")
            return redirect(url_for("dashboard"))

        req_lang = request.args.get("lang")
        if req_lang in SUPPORTED_LANGUAGES:
            session["language"] = req_lang

        cur_lang = get_current_language()
        rec_info = get_disease_recommendation(pred_record["class_name"], lang=cur_lang)

        return render_template(
            "result.html",
            status="success",
            is_low_confidence=False,
            prediction=pred_record,
            recommendation=rec_info,
            image_name=pred_record["image_name"],
            confidence=pred_record["confidence"],
            localized_crop=get_crop_display(pred_record["crop"], lang=cur_lang),
            localized_disease=get_disease_display(pred_record["class_name"], lang=cur_lang)
        )
    except Exception as e:
        flash(f"Failed to load prediction result: {e}", "danger")
        return redirect(url_for("dashboard"))

@app.route("/history")
@login_required
def history():
    """User-isolated prediction history."""
    user_id = session["user_id"]
    try:
        records = get_user_predictions(user_id)
        return render_template("history.html", predictions=records)
    except Exception as e:
        flash(f"Failed to load history: {e}", "danger")
        return render_template("history.html", predictions=[])

# ==========================================================
# CROP RECOMMENDATION ROUTES
# ==========================================================

@app.route("/crop-recommendation", methods=["GET", "POST"])
@app.route("/recommend-crop", methods=["GET", "POST"])
@login_required
def recommend_crop():
    """Precision Agriculture: Soil & Climate based Crop Recommendation."""
    if request.method == "GET":
        return render_template("crop_recommendation.html")

    user_id = session["user_id"]
    try:
        n = float(request.form.get("nitrogen", 0))
        p = float(request.form.get("phosphorus", 0))
        k = float(request.form.get("potassium", 0))
        temp = float(request.form.get("temperature", 0))
        hum = float(request.form.get("humidity", 0))
        ph = float(request.form.get("ph", 0))
        rainfall = float(request.form.get("rainfall", 0))
    except (ValueError, TypeError):
        flash("Invalid numerical values provided. Please enter valid soil and climate numbers.", "danger")
        return redirect(url_for("recommend_crop"))

    recommender = load_crop_recommender()
    if recommender is None:
        flash("Crop recommendation engine is temporarily unavailable. Please try again later.", "danger")
        return redirect(url_for("recommend_crop"))

    res = recommender.predict(n, p, k, temp, hum, ph, rainfall)
    if not res.get("success"):
        flash(res.get("error", "Failed to compute crop recommendation."), "danger")
        return redirect(url_for("recommend_crop"))

    recommended_crop = res["recommended_crop"]
    confidence = res["confidence"]
    top_suggestions = res["top_recommendations"]
    inputs = res["inputs"]

    crop_info = get_crop_catalog_info(recommended_crop)

    rec_id = save_crop_recommendation(
        user_id=user_id,
        nitrogen=n,
        phosphorus=p,
        potassium=k,
        temperature=temp,
        humidity=hum,
        ph=ph,
        rainfall=rainfall,
        recommended_crop=recommended_crop,
        confidence=confidence,
        top_suggestions=top_suggestions
    )

    return render_template(
        "crop_result.html",
        recommended_crop=recommended_crop,
        confidence=confidence,
        top_suggestions=top_suggestions,
        inputs=inputs,
        crop_info=crop_info,
        recommendation_id=rec_id
    )

@app.route("/crop-result/<int:rec_id>")
@login_required
def view_crop_result(rec_id):
    """View historical crop recommendation record."""
    user_id = session["user_id"]
    rec = get_crop_recommendation_by_id(rec_id, user_id)
    if not rec:
        flash("Crop recommendation record not found or unauthorized.", "warning")
        return redirect(url_for("crop_history"))

    crop_info = get_crop_catalog_info(rec["recommended_crop"])
    inputs = {
        "N": rec["nitrogen"], "P": rec["phosphorus"], "K": rec["potassium"],
        "temperature": rec["temperature"], "humidity": rec["humidity"],
        "ph": rec["ph"], "rainfall": rec["rainfall"]
    }
    return render_template(
        "crop_result.html",
        recommended_crop=rec["recommended_crop"],
        confidence=rec["confidence"],
        top_suggestions=rec.get("top_suggestions", []),
        inputs=inputs,
        crop_info=crop_info,
        recommendation_id=rec["id"]
    )

@app.route("/crop-history")
@login_required
def crop_history():
    """User-isolated past crop recommendation history."""
    user_id = session["user_id"]
    try:
        records = get_user_crop_recommendations(user_id)
        return render_template("crop_history.html", recommendations=records)
    except Exception as e:
        flash(f"Failed to load crop history: {e}", "danger")
        return render_template("crop_history.html", recommendations=[])

# ==========================================================
# REST API ENDPOINTS
# ==========================================================

@app.route("/api/crop/recommend", methods=["POST"])
def api_recommend_crop():
    """API endpoint for precision crop recommendation."""
    data = request.get_json() or {}
    try:
        n = float(data.get("N", data.get("nitrogen", 0)))
        p = float(data.get("P", data.get("phosphorus", 0)))
        k = float(data.get("K", data.get("potassium", 0)))
        temp = float(data.get("temperature", 0))
        hum = float(data.get("humidity", 0))
        ph = float(data.get("ph", 0))
        rainfall = float(data.get("rainfall", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid numerical parameters."}), 400

    recommender = load_crop_recommender()
    if not recommender:
        return jsonify({"success": False, "error": "Crop recommender service unavailable."}), 503

    res = recommender.predict(n, p, k, temp, hum, ph, rainfall)
    if not res.get("success"):
        return jsonify({"success": False, "error": res.get("error")}), 400

    crop_info = get_crop_catalog_info(res["recommended_crop"])
    return jsonify({
        "success": True,
        "message": "Crop recommendation calculated successfully.",
        "data": {
            "recommended_crop": res["recommended_crop"],
            "confidence": res["confidence"],
            "top_recommendations": res["top_recommendations"],
            "inputs": res["inputs"],
            "crop_information": crop_info
        }
    })

@app.route("/api/crops", methods=["GET"])
def api_crops_catalog():
    """API endpoint to list 22 supported crops catalog."""
    crops = get_all_crop_catalog()
    return jsonify({"success": True, "count": len(crops), "data": crops})

# ==========================================================
# ERROR HANDLERS
# ==========================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    flash("The uploaded image file is too large (maximum allowed size: 16 MB).", "danger")
    return redirect(url_for("predict"))

if __name__ == "__main__":
    init_db()
    load_ml_model()
    load_crop_recommender()
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
