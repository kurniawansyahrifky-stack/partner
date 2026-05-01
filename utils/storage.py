import os
import json
from config import *

DEBUG_MODE = True


def debug_log(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")


# ================= JSON =================
def load_json(file, default):
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception as e:
        debug_log(e)
        return default


def save_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        debug_log(e)


# ================= SETTING =================
def load_setting():
    return load_json(SETTING_FILE, {})


def save_setting(data):
    save_json(SETTING_FILE, data)


# ================= PARTNER =================
def load_partner():
    data = load_json(PARTNER_FILE, [])
    return [p for p in data if isinstance(p, dict)]


def save_partner(data):
    clean = [p for p in data if isinstance(p, dict)]
    save_json(PARTNER_FILE, clean)


# ================= BUTTON =================
def load_buttons():
    return load_json(BUTTON_FILE, {})


def save_buttons(data):
    save_json(BUTTON_FILE, data)


# ================= AUTOTAG =================
auto_data = {}

def load_autotag():
    global auto_data
    auto_data = load_json(AUTO_TAG_FILE, {})


def save_autotag():
    save_json(AUTO_TAG_FILE, auto_data)
