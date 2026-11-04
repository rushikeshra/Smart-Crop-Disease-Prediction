# System Requirements Specification (SRS)

## 1. Hardware Requirements

### Minimum Development Hardware:
- **Processor**: Dual-Core Intel Core i3 / AMD Ryzen 3 (Quad-Core i5 / Ryzen 5 recommended for deep learning training)
- **RAM**: 4 GB minimum (8 GB+ recommended for TensorFlow model loading)
- **Storage**: 2 GB free disk space for models, datasets, and dependencies
- **Display**: $1280 \times 720$ resolution or higher

### User Hardware (Client):
- Any modern PC, laptop, tablet, or smartphone with a modern web browser and camera.

---

## 2. Software Requirements

### Operating System:
- Windows 10/11, macOS 12+, or Ubuntu/Linux 20.04+

### Server & ML Stack:
- **Python**: Version 3.8 to 3.11
- **Flask**: Web application framework (REST API)
- **Database**: MySQL Server 8.0+ / MariaDB 10.5+ (Automated SQLite fallback enabled for local demo)
- **Machine Learning Libraries**:
  - `tensorflow` (>= 2.13.0) & `keras`
  - `scikit-learn` (>= 1.3.0)
  - `pandas` (>= 2.0.0) & `numpy` (>= 1.24.0)
  - `joblib` (>= 1.3.0)
  - `Pillow` (>= 10.0.0)

### Client / Frontend Stack:
- **Web Browser**: Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari (modern version with JavaScript enabled).
- **Frontend Architecture**: Server-side rendered HTML5 with Jinja2 templates, Bootstrap 5 CSS, FontAwesome/Bootstrap Icons, and Vanilla JavaScript (ES6).

---

## 3. Non-Functional Requirements
- **Performance**: Sub-200ms inference for Crop Recommendation; Sub-1s inference for Leaf Disease Computer Vision.
- **Reliability**: Graceful error handling for missing models, corrupt image files, unsupported formats, and missing database connections (with automated SQLite fallback).
- **Security**: Parameterized SQL queries preventing SQL injection, Werkzeug PBKDF2 cryptographic password hashing, and secure HTTP-only session cookies.
