import asyncio
import json
from datetime import datetime, timedelta, timezone

LIMIT_FILE = "limit_gc.json"
WIB = timezone(timedelta(hours=7))


def get_today_wib():
    return datetime.now(WIB).strftime("%Y-%m-%d")


async def load_limit():
    try:
        with open(LIMIT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


async def save_limit(data):
    with open(LIMIT_FILE, "w") as f:
        json.dump(data, f)


# ================= AUTO RESET =================
async def reset_limit_daily():
    while True:
        try:
            now = datetime.now(WIB)

            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            wait_time = (tomorrow - now).total_seconds()

            print(f"⏳ RESET LIMIT DALAM {int(wait_time)} DETIK")

            await asyncio.sleep(wait_time)

            await save_limit({})
            print("🔥 LIMIT GC DI RESET")

        except Exception as e:
            print("❌ ERROR RESET LIMIT:", e)
            await asyncio.sleep(60)
