-- ==========================================================
-- SMART CROP DISEASE PREDICTION SYSTEM - DATABASE SCHEMA
-- Target Database: MySQL 8.0+ / MariaDB
-- ==========================================================

CREATE DATABASE IF NOT EXISTS smart_crop_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smart_crop_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Disease Predictions Table
CREATE TABLE IF NOT EXISTS disease_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crop VARCHAR(50) NOT NULL,
    disease VARCHAR(100) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    image_name VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pred_user (user_id),
    INDEX idx_pred_class (class_name),
    INDEX idx_pred_time (timestamp),
    CONSTRAINT fk_prediction_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Disease Recommendations Table
CREATE TABLE IF NOT EXISTS disease_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NOT NULL,
    cure_treatment TEXT NOT NULL,
    chemical_information TEXT NOT NULL,
    prevention TEXT NOT NULL,
    recovery_period VARCHAR(255) NULL,
    recommendation_1 TEXT NULL,
    recommendation_2 TEXT NULL,
    INDEX idx_rec_prediction (prediction_id),
    CONSTRAINT fk_rec_prediction FOREIGN KEY (prediction_id) REFERENCES disease_predictions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Crop Recommendations Table (NPK & Climate Soil Analysis)
CREATE TABLE IF NOT EXISTS crop_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nitrogen FLOAT NOT NULL,
    phosphorus FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    ph FLOAT NOT NULL,
    rainfall FLOAT NOT NULL,
    recommended_crop VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    top_suggestions TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_crop_user (user_id),
    INDEX idx_crop_rec (recommended_crop),
    INDEX idx_crop_time (created_at),
    CONSTRAINT fk_crop_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Crop Information Table (Agronomic Catalog for 22 Crops)
CREATE TABLE IF NOT EXISTS crop_information (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(150) NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    soil_information TEXT NOT NULL,
    cultivation_information TEXT NOT NULL,
    water_requirement VARCHAR(100) NULL,
    harvest_duration VARCHAR(100) NULL,
    expected_benefits TEXT NULL,
    farming_tips TEXT NOT NULL,
    INDEX idx_crop_name (crop_name),
    INDEX idx_crop_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

