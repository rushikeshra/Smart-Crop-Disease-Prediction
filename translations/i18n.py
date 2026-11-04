# -*- coding: utf-8 -*-
"""
Centralized Multilingual i18n Translation Engine for Smart Crop AI.
Supports English (en), Hindi (hi), and Marathi (mr).
"""

import os
import json
from flask import session, has_request_context

TRANSLATIONS_DIR = os.path.dirname(os.path.abspath(__file__))
_TRANSLATIONS = {}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "mr": "मराठी"
}

def load_all_translations():
    """Load translation dictionaries into memory."""
    global _TRANSLATIONS
    for lang in ["en", "hi", "mr"]:
        file_path = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    _TRANSLATIONS[lang] = json.load(f)
            except Exception as e:
                print(f"[i18n ERROR] Failed loading {file_path}: {e}")
                _TRANSLATIONS[lang] = {}
        else:
            _TRANSLATIONS[lang] = {}

def get_current_language():
    """Get currently active language code from Flask session, default 'en'."""
    if has_request_context():
        lang = session.get("language")
        if lang and lang in SUPPORTED_LANGUAGES:
            return lang
    return "en"

def set_current_language(lang_code):
    """Store active language in Flask session."""
    if has_request_context() and lang_code in SUPPORTED_LANGUAGES:
        session["language"] = lang_code
        return True
    return False

def t(key, lang=None, **kwargs):
    """
    Lookup a localized string using dot notation (e.g. 'nav.home').
    Falls back gracefully to English, then to the key itself.
    """
    global _TRANSLATIONS
    if not _TRANSLATIONS:
        load_all_translations()

    if not lang:
        lang = get_current_language()

    lang_dict = _TRANSLATIONS.get(lang) or _TRANSLATIONS.get("en", {})
    parts = key.split(".")
    val = lang_dict

    for p in parts:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            # Fallback to English dictionary
            en_dict = _TRANSLATIONS.get("en", {})
            en_val = en_dict
            for ep in parts:
                if isinstance(en_val, dict) and ep in en_val:
                    en_val = en_val[ep]
                else:
                    return key
            val = en_val
            break

    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val

    return val

def get_crop_display(crop_name, lang=None):
    """Translate crop name for display while preserving scientific/internal identification."""
    if not lang:
        lang = get_current_language()

    norm_key = crop_name.split("(")[0].strip().replace(" ", "_")
    localized = t(f"crops.{norm_key}", lang=lang)
    if localized != f"crops.{norm_key}":
        return localized
    return crop_name

def get_disease_display(class_name, lang=None):
    """Translate disease name for display while preserving scientific/internal identification."""
    if not lang:
        lang = get_current_language()

    localized = t(f"diseases.{class_name}", lang=lang)
    if localized != f"diseases.{class_name}":
        return localized
    
    clean = class_name.split("___")[-1].replace("_", " ").title()
    if "Healthy" in clean:
        return "Healthy Foliage"
    return clean

# Initial load at module import
load_all_translations()
