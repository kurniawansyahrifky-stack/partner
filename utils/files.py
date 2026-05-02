import os
import json
import aiofiles
from config import *

# ================= CORE JSON =================
async def load_json(file, default):
    if not os.path.exists(file):
        return default
    try:
        async with aiofiles.open(file, "r") as f:
            return json.loads(await f.read())
    except Exception as e:
        print(f"[LOAD ERROR] {file}: {e}")
        return default

async def save_json(file, data):
    try:
        async with aiofiles.open(file, "w") as f:
            await f.write(json.dumps(data, indent=2))
    except Exception as e:
        print(f"[SAVE ERROR] {file}: {e}")


# ================= SETTING =================
async def load_setting():
    return await load_json(SETTING_FILE, {})

async def save_setting(data):
    await save_json(SETTING_FILE, data)


# ================= PARTNER =================
async def load_partner():
    data = await load_json(PARTNER_FILE, [])
    return [p for p in data if isinstance(p, dict)]

async def save_partner(data):
    clean = [p for p in data if isinstance(p, dict)]
    await save_json(PARTNER_FILE, clean)


# ================= BUTTON =================
async def load_buttons():
    return await load_json(BUTTON_FILE, {})

async def save_buttons(data):
    await save_json(BUTTON_FILE, data)


# ================= AUTOTAG =================
async def load_autotag():
    return await load_json(AUTO_TAG_FILE, {})

async def save_autotag(data):
    await save_json(AUTO_TAG_FILE, data)


# ================= QUEUE =================
async def load_queue():
    return await load_json(QUEUE_FILE, [])

async def save_queue(data):
    await save_json(QUEUE_FILE, data)
