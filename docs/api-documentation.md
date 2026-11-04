# Application Routes & REST API Specification

Base Server URL: `http://127.0.0.1:5000`

---

## 1. Web Application Routes (MVC / Jinja2)

### 1.1 Authentication & Navigation
| Route | Methods | Description | Access |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Landing hero page with overview and crop coverage | Public |
| `/register` | `GET`, `POST` | User registration with validation and password hashing | Public |
| `/login` | `GET`, `POST` | User login creating secure session cookie | Public |
| `/logout` | `GET` | Clears user session and redirects to login | Authenticated |
| `/dashboard` | `GET` | Overview statistics, recent leaf scans, and recent soil recommendations | Authenticated |

### 1.2 Disease Diagnosis Routes
| Route | Methods | Description | Access |
| :--- | :--- | :--- | :--- |
| `/predict` | `GET` | Renders leaf photo drag & drop upload interface | Authenticated |
| `/predict` | `POST` | Processes uploaded leaf image, runs MobileNetV2 inference, saves record, renders `result.html` | Authenticated |
| `/result/<id>` | `GET` | View previously saved diagnosis and agronomic advisories by prediction ID | Authenticated |
| `/history` | `GET` | User-isolated table of all past leaf diagnoses with thumbnails and confidence scores | Authenticated |

### 1.3 Crop Recommendation Routes
| Route | Methods | Description | Access |
| :--- | :--- | :--- | :--- |
| `/recommend-crop` | `GET` | Form to input soil parameters ($N, P, K$, Temp, Humidity, pH, Rainfall) | Authenticated |
| `/crop-recommendation` | `GET` | Alias for `/recommend-crop` | Authenticated |
| `/recommend-crop` | `POST` | Validates soil numbers, runs Random Forest model, saves record, renders `crop_result.html` | Authenticated |
| `/crop-result/<id>` | `GET` | View previously saved crop recommendation with cultivation guidelines | Authenticated |
| `/crop-history` | `GET` | User-isolated table of past soil analyses and recommended crops | Authenticated |

---

## 2. Programmatic REST API Endpoints (`/api`)

### 2.1 Recommend Crop via JSON
- **Endpoint**: `POST /api/crop/recommend`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.8,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.9
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Crop recommendation computed successfully.",
    "data": {
      "recommended_crop": "rice",
      "confidence": 84.09,
      "top_recommendations": [
        { "crop": "rice", "confidence": 84.09 },
        { "crop": "jute", "confidence": 13.91 },
        { "crop": "watermelon", "confidence": 1.0 }
      ],
      "inputs": {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
      },
      "crop_information": {
        "crop_name": "rice",
        "scientific_name": "Oryza sativa",
        "category": "Cereals",
        "description": "Rice is the primary staple food for over half of the world's population...",
        "soil_information": "Thrives in deep, fertile clayey or heavy loamy soils...",
        "cultivation_information": "Seeds are typically raised in wet nurseries for 20-30 days...",
        "water_requirement": "High (1000 - 1500 mm)",
        "harvest_duration": "100 - 150 days",
        "farming_tips": "Practice alternate wetting and drying (AWD) to conserve water..."
      }
    }
  }
  ```

### 2.2 Crop Catalog Information
- **Endpoint**: `GET /api/crops`
- **Query Parameters**: Optional `?category=Cereals`
- **Response (200 OK)**: Returns list of crops in catalog with scientific names and descriptions.

