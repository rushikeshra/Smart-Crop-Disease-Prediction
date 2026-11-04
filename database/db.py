import os
import sys
import json
import sqlite3
import pymysql
from pymysql.cursors import DictCursor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config

DB_ENGINE = "mysql"  # will fallback to sqlite if mysql is unreachable

def test_mysql_connection():
    """Check if MySQL is reachable with configured credentials."""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception as e:
        return False

def get_sqlite_conn():
    db_file = os.path.join(os.path.dirname(__file__), "smart_crop.db")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection(use_database=True):
    """Establish connection to database (MySQL with fallback)."""
    global DB_ENGINE
    if DB_ENGINE == "mysql":
        try:
            db_name = Config.MYSQL_DATABASE if use_database else None
            return pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=db_name,
                cursorclass=DictCursor,
                autocommit=True,
                charset="utf8mb4"
            )
        except Exception as e:
            print(f"[DB NOTICE] MySQL connection failed: {e}. Switching to local storage engine.")
            DB_ENGINE = "sqlite"
            return get_sqlite_conn()
    else:
        return get_sqlite_conn()

def init_db():
    """Create database and tables if they do not exist."""
    global DB_ENGINE
    print("[DB] Initializing Database Schema...")

    # Check MySQL first
    if test_mysql_connection():
        DB_ENGINE = "mysql"
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                cursorclass=DictCursor,
                autocommit=True
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                cursor.execute(f"USE `{Config.MYSQL_DATABASE}`;")
                
                schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()

                statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
                for stmt in statements:
                    clean_lines = [line for line in stmt.splitlines() if not line.strip().startswith("--")]
                    clean_stmt = "\n".join(clean_lines).strip()
                    if not clean_stmt:
                        continue
                    if clean_stmt.upper().startswith("CREATE DATABASE") or clean_stmt.upper().startswith("USE"):
                        continue
                    cursor.execute(clean_stmt)
                    
            conn.close()
            print(f"[DB SUCCESS] MySQL Database '{Config.MYSQL_DATABASE}' and tables initialized successfully.")
            return True
        except Exception as e:
            print(f"[DB ERROR] MySQL initialization error: {e}")
            DB_ENGINE = "sqlite"

    print("[DB INFO] Initializing SQLite database as local storage...")
    DB_ENGINE = "sqlite"
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        crop TEXT NOT NULL,
        disease TEXT NOT NULL,
        class_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        image_name TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER NOT NULL,
        cure_treatment TEXT NOT NULL,
        chemical_information TEXT NOT NULL,
        prevention TEXT NOT NULL,
        recovery_period TEXT,
        recommendation_1 TEXT,
        recommendation_2 TEXT,
        FOREIGN KEY (prediction_id) REFERENCES disease_predictions(id) ON DELETE CASCADE
    );
    """)

    # Auto-migration check for existing SQLite databases
    try:
        cursor.execute("PRAGMA table_info(disease_recommendations);")
        existing_cols = [row[1] for row in cursor.fetchall()]
        if "recovery_period" not in existing_cols:
            cursor.execute("ALTER TABLE disease_recommendations ADD COLUMN recovery_period TEXT;")
        if "recommendation_1" not in existing_cols:
            cursor.execute("ALTER TABLE disease_recommendations ADD COLUMN recommendation_1 TEXT;")
        if "recommendation_2" not in existing_cols:
            cursor.execute("ALTER TABLE disease_recommendations ADD COLUMN recommendation_2 TEXT;")
        conn.commit()
    except Exception as e:
        print(f"[DB NOTICE] Migration check notice: {e}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nitrogen REAL NOT NULL,
        phosphorus REAL NOT NULL,
        potassium REAL NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        ph REAL NOT NULL,
        rainfall REAL NOT NULL,
        recommended_crop TEXT NOT NULL,
        confidence REAL NOT NULL,
        top_suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_information (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL UNIQUE,
        scientific_name TEXT,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        soil_information TEXT NOT NULL,
        cultivation_information TEXT NOT NULL,
        water_requirement TEXT,
        harvest_duration TEXT,
        expected_benefits TEXT,
        farming_tips TEXT NOT NULL
    );
    """)

    # Seed 22 crops catalog into crop_information
    try:
        from database.seed_data import CROPS_CATALOG
        for c in CROPS_CATALOG:
            cursor.execute("""
                INSERT OR IGNORE INTO crop_information 
                (crop_name, scientific_name, category, description, soil_information, cultivation_information, water_requirement, harvest_duration, expected_benefits, farming_tips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["crop_name"], c.get("scientific_name"), c["category"], c["description"],
                c["soil_information"], c["cultivation_information"], c.get("water_requirement"),
                c.get("harvest_duration"), c.get("expected_benefits"), c["farming_tips"]
            ))
        conn.commit()
    except Exception as e:
        print(f"[DB NOTICE] Crop catalog auto-seeding notice: {e}")

    # Ensure default admin & demo users exist
    try:
        from werkzeug.security import generate_password_hash
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        row_count = cursor.fetchone()[0] if cursor else 0
        if row_count == 0:
            cursor.execute(
                "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Admin User", "admin@smartcrop.com", generate_password_hash("admin123"))
            )
            cursor.execute(
                "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo Farmer", "farmer@smartcrop.com", generate_password_hash("Password123!"))
            )
            conn.commit()
            print("[DB SUCCESS] Seeded default credentials: admin@smartcrop.com and farmer@smartcrop.com")
    except Exception as e:
        print(f"[DB NOTICE] User auto-seeding notice: {e}")

    conn.close()
    print("[DB SUCCESS] Database tables verified/created successfully.")
    return True

# ==========================================================
# USER OPERATIONS
# ==========================================================

def create_user(name, email, password_hash):
    """Insert new user into database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            sql = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email.strip().lower(), password_hash))
            uid = cursor.lastrowid
        else:
            sql = "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)"
            cursor.execute(sql, (name, email.strip().lower(), password_hash))
            conn.commit()
            uid = cursor.lastrowid
        return uid
    finally:
        conn.close()

def get_user_by_email(email):
    """Retrieve user record by email."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email.strip().lower(),))
            return cursor.fetchone()
        else:
            sql = "SELECT * FROM users WHERE email = ?"
            cursor.execute(sql, (email.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Retrieve user record by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            sql = "SELECT id, name, email, created_at FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
        else:
            sql = "SELECT id, name, email, created_at FROM users WHERE id = ?"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

# ==========================================================
# PREDICTION & RECOMMENDATION OPERATIONS
# ==========================================================

def save_prediction(user_id, crop, disease, class_name, confidence, image_name, cure_treatment, chemical_info, prevention, recovery_period=None, recommendation_1=None, recommendation_2=None):
    """Save prediction and corresponding recommendation atomically."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if DB_ENGINE == "mysql":
            pred_sql = """
                INSERT INTO disease_predictions 
                (user_id, crop, disease, class_name, confidence, image_name) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(pred_sql, (user_id, crop, disease, class_name, float(confidence), image_name))
            prediction_id = cursor.lastrowid

            rec_sql = """
                INSERT INTO disease_recommendations 
                (prediction_id, cure_treatment, chemical_information, prevention, recovery_period, recommendation_1, recommendation_2) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(rec_sql, (prediction_id, cure_treatment, chemical_info, prevention, recovery_period, recommendation_1, recommendation_2))
            return prediction_id
        else:
            pred_sql = """
                INSERT INTO disease_predictions 
                (user_id, crop, disease, class_name, confidence, image_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(pred_sql, (user_id, crop, disease, class_name, float(confidence), image_name))
            prediction_id = cursor.lastrowid

            rec_sql = """
                INSERT INTO disease_recommendations 
                (prediction_id, cure_treatment, chemical_information, prevention, recovery_period, recommendation_1, recommendation_2) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(rec_sql, (prediction_id, cure_treatment, chemical_info, prevention, recovery_period, recommendation_1, recommendation_2))
            conn.commit()
            return prediction_id
    finally:
        conn.close()

def get_user_predictions(user_id, limit=None):
    """Retrieve prediction history for a specific user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        sql = f"""
            SELECT p.id, p.user_id, p.crop, p.disease, p.class_name, p.confidence, 
                   p.image_name, p.timestamp,
                   r.cure_treatment, r.chemical_information, r.prevention,
                   r.recovery_period, r.recommendation_1, r.recommendation_2
            FROM disease_predictions p
            LEFT JOIN disease_recommendations r ON p.id = r.prediction_id
            WHERE p.user_id = {placeholder}
            ORDER BY p.timestamp DESC
        """
        if limit:
            sql += f" LIMIT {int(limit)}"
        cursor.execute(sql, (user_id,))
        if DB_ENGINE == "mysql":
            return cursor.fetchall()
        else:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

def get_prediction_by_id(prediction_id, user_id):
    """Retrieve a single prediction ensuring user ownership."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        sql = f"""
            SELECT p.id, p.user_id, p.crop, p.disease, p.class_name, p.confidence, 
                   p.image_name, p.timestamp,
                   r.cure_treatment, r.chemical_information, r.prevention,
                   r.recovery_period, r.recommendation_1, r.recommendation_2
            FROM disease_predictions p
            LEFT JOIN disease_recommendations r ON p.id = r.prediction_id
            WHERE p.id = {placeholder} AND p.user_id = {placeholder}
        """
        cursor.execute(sql, (prediction_id, user_id))
        if DB_ENGINE == "mysql":
            return cursor.fetchone()
        else:
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def get_user_statistics(user_id):
    """Get dashboard stats for user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        
        # Total predictions
        cursor.execute(f"SELECT COUNT(*) as total FROM disease_predictions WHERE user_id = {placeholder}", (user_id,))
        row = cursor.fetchone()
        total_preds = row["total"] if DB_ENGINE == "mysql" else row[0]

        # Top detected disease
        cursor.execute(f"""
            SELECT disease, COUNT(*) as count 
            FROM disease_predictions 
            WHERE user_id = {placeholder} 
            GROUP BY disease 
            ORDER BY count DESC 
            LIMIT 1
        """, (user_id,))
        top_disease_row = cursor.fetchone()
        top_disease = top_disease_row["disease"] if top_disease_row else "None yet"

        # Latest prediction
        cursor.execute(f"""
            SELECT crop, disease, confidence, timestamp 
            FROM disease_predictions 
            WHERE user_id = {placeholder} 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (user_id,))
        last_pred_row = cursor.fetchone()
        last_pred = dict(last_pred_row) if last_pred_row else None

        # Predictions grouped by crop
        cursor.execute(f"""
            SELECT crop, COUNT(*) as count 
            FROM disease_predictions 
            WHERE user_id = {placeholder} 
            GROUP BY crop
        """, (user_id,))
        if DB_ENGINE == "mysql":
            crop_distribution = cursor.fetchall()
        else:
            crop_distribution = [dict(r) for r in cursor.fetchall()]

        # Crop recommendations count for user
        cursor.execute(f"SELECT COUNT(*) as total FROM crop_recommendations WHERE user_id = {placeholder}", (user_id,))
        crop_row = cursor.fetchone()
        total_crops = crop_row["total"] if DB_ENGINE == "mysql" else crop_row[0]

        # Latest crop recommendation
        cursor.execute(f"""
            SELECT recommended_crop, confidence, created_at 
            FROM crop_recommendations 
            WHERE user_id = {placeholder} 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        last_crop_row = cursor.fetchone()
        last_crop = dict(last_crop_row) if last_crop_row else None

        return {
            "total_predictions": total_preds,
            "total_crop_recommendations": total_crops,
            "top_disease": top_disease,
            "last_prediction": last_pred,
            "last_crop_recommendation": last_crop,
            "crop_distribution": crop_distribution,
            "supported_crops_count": 7,
            "recommendation_crops_count": 22
        }
    finally:
        conn.close()

# ==========================================================
# DISEASE KNOWLEDGE BASE LOOKUP
# ==========================================================

def get_disease_recommendation(class_name, lang=None):
    """Retrieve disease recommendation details from JSON knowledge base with multi-language support."""
    json_path = Config.DISEASE_INFO_PATH
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        info = None
        if class_name in data:
            info = data[class_name]
        else:
            # Robust normalization for underscores, dashes, and casing
            norm_target = class_name.lower().replace("___", "_").replace("_", "").replace("-", "").replace(" ", "").replace("(maize)", "").replace("(corn)", "")
            for k, v in data.items():
                norm_k = k.lower().replace("___", "_").replace("_", "").replace("-", "").replace(" ", "").replace("(maize)", "").replace("(corn)", "")
                if norm_k == norm_target:
                    info = v
                    break

        if not info:
            return None

        # Determine target language
        if lang is None:
            try:
                from flask import session, has_request_context
                if has_request_context():
                    lang = session.get("language", "en")
                else:
                    lang = "en"
            except Exception:
                lang = "en"

        if lang not in ["en", "hi", "mr"]:
            lang = "en"

        # If localized translation is requested and available, return localized view
        translations = info.get("translations", {})
        if lang != "en" and lang in translations:
            localized = dict(info)
            loc = translations[lang]
            for key in ["crop_name", "disease_name", "description", "symptoms", "prevention", "treatment_or_cure", "recovery_period", "recommendation_1", "recommendation_2", "chemical_information", "disclaimer"]:
                if key in loc and loc[key]:
                    localized[key] = loc[key]
            return localized

        return info
    except Exception as e:
        print(f"[ERROR] Failed to load disease info for {class_name}: {e}")
        return None

# ==========================================================
# CROP RECOMMENDATION OPERATIONS
# ==========================================================

def save_crop_recommendation(user_id, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, recommended_crop, confidence, top_suggestions=None):
    """Save crop recommendation result for user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        suggestions_json = json.dumps(top_suggestions) if top_suggestions else None
        
        sql = f"""
            INSERT INTO crop_recommendations 
            (user_id, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, recommended_crop, confidence, top_suggestions)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        cursor.execute(sql, (
            user_id, float(nitrogen), float(phosphorus), float(potassium),
            float(temperature), float(humidity), float(ph), float(rainfall),
            str(recommended_crop), float(confidence), suggestions_json
        ))
        if hasattr(conn, "commit"):
            conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_user_crop_recommendations(user_id, limit=None):
    """Get all past crop recommendations for a user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        sql = f"""
            SELECT id, user_id, nitrogen, phosphorus, potassium, 
                   temperature, humidity, ph, rainfall, 
                   recommended_crop, confidence, top_suggestions, created_at
            FROM crop_recommendations
            WHERE user_id = {placeholder}
            ORDER BY created_at DESC
        """
        if limit:
            sql += f" LIMIT {int(limit)}"
        cursor.execute(sql, (user_id,))
        if DB_ENGINE == "mysql":
            rows = cursor.fetchall()
        else:
            rows = [dict(r) for r in cursor.fetchall()]
        
        # Parse top_suggestions JSON
        for r in rows:
            if r.get("top_suggestions"):
                try:
                    r["top_suggestions"] = json.loads(r["top_suggestions"])
                except Exception:
                    r["top_suggestions"] = []
            else:
                r["top_suggestions"] = []
        return rows
    finally:
        conn.close()

def get_crop_recommendation_by_id(rec_id, user_id):
    """Retrieve a single crop recommendation record ensuring user isolation."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        sql = f"""
            SELECT id, user_id, nitrogen, phosphorus, potassium, 
                   temperature, humidity, ph, rainfall, 
                   recommended_crop, confidence, top_suggestions, created_at
            FROM crop_recommendations
            WHERE id = {placeholder} AND user_id = {placeholder}
        """
        cursor.execute(sql, (rec_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None
        rec = dict(row) if DB_ENGINE != "mysql" else row
        if rec.get("top_suggestions"):
            try:
                rec["top_suggestions"] = json.loads(rec["top_suggestions"])
            except Exception:
                rec["top_suggestions"] = []
        return rec
    finally:
        conn.close()

def get_crop_catalog_info(crop_name):
    """Fetch agronomic guidelines for crop from database or catalog fallback."""
    clean_name = str(crop_name).strip().lower()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = "%s" if DB_ENGINE == "mysql" else "?"
        cursor.execute(f"SELECT * FROM crop_information WHERE LOWER(crop_name) = {placeholder}", (clean_name,))
        row = cursor.fetchone()
        if row:
            return dict(row) if DB_ENGINE != "mysql" else row
    except Exception as e:
        print(f"[DB ERROR] Error fetching crop info from DB: {e}")
    finally:
        conn.close()

    # Fallback to CROPS_CATALOG in seed_data
    try:
        from database.seed_data import CROPS_CATALOG
        for item in CROPS_CATALOG:
            if item["crop_name"].lower() == clean_name:
                return item
    except Exception:
        pass

    return {
        "crop_name": clean_name.capitalize(),
        "scientific_name": "Agri-crop",
        "category": "Field Crop",
        "description": f"Agronomic guide for optimal cultivation of {clean_name.capitalize()}.",
        "soil_information": "Thrives in well-drained, fertile soil with balanced organic matter.",
        "cultivation_information": "Prepare seedbed thoroughly and ensure uniform row planting.",
        "water_requirement": "Moderate irrigation depending on seasonal rainfall.",
        "harvest_duration": "90 - 120 days",
        "expected_benefits": "High yield and solid economic return when managed with balanced NPK.",
        "farming_tips": "Practice regular field weeding and monitor soil moisture."
    }

def get_all_crop_catalog():
    """Retrieve full catalog of supported crops."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT crop_name, scientific_name, category, description, harvest_duration FROM crop_information ORDER BY crop_name ASC")
        if DB_ENGINE == "mysql":
            return cursor.fetchall()
        else:
            return [dict(r) for r in cursor.fetchall()]
    except Exception:
        from database.seed_data import CROPS_CATALOG
        return CROPS_CATALOG
    finally:
        conn.close()

