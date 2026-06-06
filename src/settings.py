# -*- coding: utf-8 -*-
import os
import json
import sys

def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = _app_dir()
RESIMLER_DIR = os.path.join(APP_DIR, "resimler")

# ─── Language / Translation support ───
import json

_SETTINGS_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "PDF_Create_Export_Edit")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

def _load_settings():
    try:
        with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_settings(data):
    try:
        os.makedirs(_SETTINGS_DIR, exist_ok=True)
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
