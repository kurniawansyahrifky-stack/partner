import os
import time
import shutil
import zipfile

from config import *

LAST_BACKUP = None

CORE_FILES = [
    "setting.json5",
    "partner.json9",
    "buttons.json5",
    "autotag.json5"
]


# ================= ROLLBACK =================
async def rollback_last_backup(client, message):
    global LAST_BACKUP

    if not LAST_BACKUP or not os.path.exists(LAST_BACKUP):
        await message.reply("❌ tidak ada backup")
        return

    try:
        await message.reply("🔁 rollback...")

        for f in CORE_FILES:
            if os.path.exists(f):
                os.remove(f)

        if os.path.exists("database9"):
            shutil.rmtree("database9")

        with zipfile.ZipFile(LAST_BACKUP, 'r') as z:
            z.extractall()

        await message.reply("✅ rollback sukses")

    except Exception as e:
        await message.reply(f"❌ rollback gagal: {e}")


# ================= RESTORE =================
async def restore_cmd(client, message):
    global LAST_BACKUP

    if message.from_user.id not in OWNER_IDS:
        await message.reply("❌ bukan owner")
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("❌ reply file zip")
        return

    try:
        await message.reply("⏳ restore...")

        file = await message.reply_to_message.download("restore.zip")

        if not zipfile.is_zipfile(file):
            await message.reply("❌ zip rusak")
            return

        with zipfile.ZipFile(file, 'r') as z:
            files = z.namelist()

            if not any(f in files for f in CORE_FILES):
                await message.reply("❌ struktur salah")
                return

            LAST_BACKUP = f"backup_{int(time.time())}.zip"

            with zipfile.ZipFile(LAST_BACKUP, 'w', zipfile.ZIP_DEFLATED) as backup:
                for f in CORE_FILES:
                    if os.path.exists(f):
                        backup.write(f)

                if os.path.exists("database9"):
                    for root, _, files2 in os.walk("database9"):
                        for f in files2:
                            backup.write(os.path.join(root, f))

            for f in CORE_FILES:
                if os.path.exists(f):
                    os.remove(f)

            if os.path.exists("database9"):
                shutil.rmtree("database9")

            z.extractall()

        await message.reply("✅ restore sukses")

    except Exception as e:
        await message.reply(f"❌ restore gagal: {e}")
