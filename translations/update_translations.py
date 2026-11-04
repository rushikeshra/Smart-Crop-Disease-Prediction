import json
import os

TRANSLATIONS_DIR = os.path.dirname(os.path.abspath(__file__))

NEW_RESULT_KEYS = {
    "en": {
        "recovery_period_title": "Expected Recovery / Management Period",
        "recommendation_1_title": "Recommendation 1 (Primary Management Option)",
        "recommendation_1_badge": "Option 1",
        "recommendation_2_title": "Recommendation 2 (Alternative Management Option)",
        "recommendation_2_badge": "Option 2",
        "supportive_management": "Supportive Cultural Practices & Hygiene"
    },
    "hi": {
        "recovery_period_title": "अपेक्षित सुधार / प्रबंधन अवधि (Recovery Period)",
        "recommendation_1_title": "सिफारिश 1 (प्राथमिक प्रबंधन विकल्प)",
        "recommendation_1_badge": "विकल्प 1",
        "recommendation_2_title": "सिफारिश 2 (वैकल्पिक प्रबंधन विकल्प)",
        "recommendation_2_badge": "विकल्प 2",
        "supportive_management": "सहायक संवर्धन पद्धतियां और स्वच्छता"
    },
    "mr": {
        "recovery_period_title": "अपेक्षित सुधारणा / व्यवस्थापन कालावधी (Recovery Period)",
        "recommendation_1_title": "शिफारस १ (प्राथमिक व्यवस्थापन पर्याय)",
        "recommendation_1_badge": "पर्याय १",
        "recommendation_2_title": "शिफारस २ (पर्यायी व्यवस्थापन पर्याय)",
        "recommendation_2_badge": "पर्याय २",
        "supportive_management": "पूरक कृषी पद्धती आणि बागेची स्वच्छता"
    }
}

NEW_CROPS = {
    "en": {
        "Green_Gram": "Green Gram (Vigna radiata)",
        "Green Gram": "Green Gram (Vigna radiata)",
        "Cotton": "Cotton (Gossypium spp.)",
        "Pigeon_Pea": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "Pigeon Pea": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "pigeonpeas": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "mungbean": "Green Gram (Vigna radiata)"
    },
    "hi": {
        "Green_Gram": "मूंग (Green Gram - Vigna radiata)",
        "Green Gram": "मूंग (Green Gram - Vigna radiata)",
        "Cotton": "कपास (Cotton - Gossypium spp.)",
        "Pigeon_Pea": "अरहर / तुअर (Pigeon Pea - Cajanus cajan)",
        "Pigeon Pea": "अरहर / तुअर (Pigeon Pea - Cajanus cajan)",
        "pigeonpeas": "अरहर / तुअर (Pigeon Pea - Cajanus cajan)",
        "mungbean": "मूंग (Green Gram - Vigna radiata)"
    },
    "mr": {
        "Green_Gram": "मूग (Green Gram - Vigna radiata)",
        "Green Gram": "मूग (Green Gram - Vigna radiata)",
        "Cotton": "कापूस (Cotton - Gossypium spp.)",
        "Pigeon_Pea": "तूर (Pigeon Pea - Cajanus cajan)",
        "Pigeon Pea": "तूर (Pigeon Pea - Cajanus cajan)",
        "pigeonpeas": "तूर (Pigeon Pea - Cajanus cajan)",
        "mungbean": "मूग (Green Gram - Vigna radiata)"
    }
}

NEW_DISEASES = {
    "en": {
        "Green_Gram___Cercospora_leaf_spot": "Cercospora Leaf Spot (Cercospora canescens)",
        "Green_Gram___Yellow_mosaic": "Yellow Mosaic Virus (MYMV)",
        "Green_Gram___Powdery_mildew": "Powdery Mildew (Erysiphe polygoni)",
        "Green_Gram___healthy": "Healthy Foliage",
        "Cotton___Bacterial_blight": "Bacterial Blight / Angular Leaf Spot (Xanthomonas citri)",
        "Cotton___Leaf_curl_virus": "Cotton Leaf Curl Virus (CLCuD)",
        "Cotton___Alternaria_leaf_spot": "Alternaria Leaf Spot (Alternaria macrospora)",
        "Cotton___healthy": "Healthy Foliage",
        "Pigeon_Pea___Sterility_mosaic": "Sterility Mosaic Disease (PPSMV)",
        "Pigeon_Pea___Phytophthora_blight": "Phytophthora Blight (Phytophthora cajani)",
        "Pigeon_Pea___Cercospora_leaf_spot": "Cercospora Leaf Spot (Cercospora indica)",
        "Pigeon_Pea___healthy": "Healthy Foliage"
    },
    "hi": {
        "Green_Gram___Cercospora_leaf_spot": "सर्कोस्पोरा पत्ती धब्बा (Cercospora canescens)",
        "Green_Gram___Yellow_mosaic": "पीला मोज़ेक वायरस (MYMV)",
        "Green_Gram___Powdery_mildew": "पाउडरी मिल्ड्यू / चूर्णिल आसिता (Erysiphe polygoni)",
        "Green_Gram___healthy": "स्वस्थ पत्तियां (Healthy Foliage)",
        "Cotton___Bacterial_blight": "जीवाणु झुलसा / कोणीय धब्बा (Xanthomonas citri)",
        "Cotton___Leaf_curl_virus": "पत्ता मरोड़ वायरस (Leaf Curl Virus)",
        "Cotton___Alternaria_leaf_spot": "अल्टरनेरिया पत्ती धब्बा (Alternaria macrospora)",
        "Cotton___healthy": "स्वस्थ पत्तियां (Healthy Foliage)",
        "Pigeon_Pea___Sterility_mosaic": "बांझपन मोज़ेक रोग (Sterility Mosaic Disease)",
        "Pigeon_Pea___Phytophthora_blight": "फाइटोफ्थोरा झुलसा (Phytophthora cajani)",
        "Pigeon_Pea___Cercospora_leaf_spot": "सर्कोस्पोरा पत्ती धब्बा (Cercospora indica)",
        "Pigeon_Pea___healthy": "स्वस्थ पत्तियां (Healthy Foliage)"
    },
    "mr": {
        "Green_Gram___Cercospora_leaf_spot": "सार्कोस्पोरा पानांवरील ठिपके (Cercospora canescens)",
        "Green_Gram___Yellow_mosaic": "पिवळा मोझॅक विषाणू (MYMV)",
        "Green_Gram___Powdery_mildew": "भुरी रोग (Erysiphe polygoni)",
        "Green_Gram___healthy": "निरोगी पाने (Healthy Foliage)",
        "Cotton___Bacterial_blight": "जिवाणूजन्य करपा / कोनीय ठिपके (Xanthomonas citri)",
        "Cotton___Leaf_curl_virus": "चुरडा-मुरडा / लीफ कर्ल (Leaf Curl Virus)",
        "Cotton___Alternaria_leaf_spot": "अल्टरनेरिया पानांवरील ठिपके (Alternaria macrospora)",
        "Cotton___healthy": "निरोगी पाने (Healthy Foliage)",
        "Pigeon_Pea___Sterility_mosaic": "वांझ रोग / स्टेरिलिटी मोझॅक (Sterility Mosaic)",
        "Pigeon_Pea___Phytophthora_blight": "फायटोप्थोरा करपा (Phytophthora cajani)",
        "Pigeon_Pea___Cercospora_leaf_spot": "सार्कोस्पोरा पानांवरील ठिपके (Cercospora indica)",
        "Pigeon_Pea___healthy": "निरोगी पाने (Healthy Foliage)"
    }
}

for lang in ["en", "hi", "mr"]:
    file_path = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Update result section
    data.setdefault("result", {}).update(NEW_RESULT_KEYS[lang])

    # 2. Update crops section
    data.setdefault("crops", {}).update(NEW_CROPS[lang])

    # 3. Update diseases section
    data.setdefault("diseases", {}).update(NEW_DISEASES[lang])

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {file_path}")

print("All translation files successfully updated!")
