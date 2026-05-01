from pyrogram import filters
from bot.client import app
from config import OWNER_IDS

import time
import os
import zipfile

from bot.utils.files import (
    load_setting, save_setting,
    load_partner, save_partner
)
from bot.utils.helpers import normalize_link, get_group_name


# ================= LIVECHAT =================
@app.on_message(filters.command("addlivechat") & filters.user(OWNER_IDS))
async def add_livechat(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ kirim link\nContoh: /addlivechat https://t.me/xxxx"
        )

    link = message.command[1]

    if not link.startswith("https://t.me/"):
        return await message.reply("❌ link harus https://t.me/")

    data = await load_setting()
    data["livechat"] = link
    await save_setting(data)

    await message.reply("✅ Live chat disimpan")


@app.on_message(filters.command("dellivechat") & filters.user(OWNER_IDS))
async def del_livechat(client, message):
    data = await load_setting()
    data.pop("livechat", None)
    await save_setting(data)

    await message.reply("✅ Live chat dihapus")


# ================= BACKUP =================
CORE_FILES = [
    "partner.json",
    "setting.json",
    "queue.json",
    "autotag.json",
    "buttons.json"
]

LAST_BACKUP = None


@app.on_message(filters.command("backup") & filters.user(OWNER_IDS))
async def backup_cmd(client, message):
    global LAST_BACKUP

    try:
        await message.reply("📦 membuat backup...")

        name = f"manual_backup_{int(time.time())}.zip"

        with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
            for f in CORE_FILES:
                if os.path.exists(f):
                    z.write(f)

            if os.path.exists("database0"):
                for root, _, files in os.walk("database0"):
                    for f in files:
                        z.write(os.path.join(root, f))

        LAST_BACKUP = name

        await message.reply_document(name, file_name=name)
        await message.reply("✅ backup manual selesai")

    except Exception as e:
        await message.reply(f"❌ backup gagal: {e}")


# ================= PARTNER =================
@app.on_message(filters.command("addpartner") & filters.user(OWNER_IDS))
async def add_partner(client, message):

    if len(message.command) < 2:
        return await message.reply(
            "❌ format:\n/addpartner nama link\natau /addpartner link"
        )

    text = message.text.replace("/addpartner", "", 1).strip()

    data = await load_partner()

    parts = text.rsplit(" ", 1)

    if len(parts) == 2:
        name_input, link = parts
    else:
        link = parts[0]
        name_input = None

    if not link.startswith("http"):
        return await message.reply("❌ link tidak valid")

    # cek duplikat
    for p in data:
        if link in p.get("link", ""):
            return await message.reply("⚠️ sudah ada")

    # ================= PRIVATE =================
    if "t.me/+" in link or "joinchat" in link:
        name = name_input if name_input else "Private Group"

        data.append({
            "link": link,
            "username": "private",
            "name": name
        })

        await save_partner(data)
        return await message.reply(f"✅ Partner private ditambah:\n{name}")

    # ================= PUBLIC =================
    username = normalize_link(link)

    name = name_input if name_input else await get_group_name(client, link)

    data.append({
        "link": f"https://t.me/{username}",
        "username": username,
        "name": name
    })

    await save_partner(data)

    await message.reply(f"✅ Partner ditambah:\n{name}")


@app.on_message(filters.command("delpartner") & filters.user(OWNER_IDS))
async def del_partner(client, message):

    if len(message.command) < 2:
        return await message.reply("❌ format: /delpartner link")

    link = message.command[1]

    data = await load_partner()

    new_data = [p for p in data if link not in p.get("link", "")]

    await save_partner(new_data)

    await message.reply("✅ Partner dihapus")
