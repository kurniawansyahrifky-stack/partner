from pyrogram import filters
from main import app
from config import OWNER_IDS, TARGET_CHATS

from utils.files import load_partner, save_partner, save_buttons
from utils.helpers import normalize_link
from utils.state import custom_buttons

import random


# 🔥 pengganti context.user_data
edit_state = {}


# ================= HANDLE EDIT =================
@app.on_message(filters.text & filters.private)
async def handle_edit(client, message):
    user_id = message.from_user.id

    # ❌ kalau bukan mode edit → skip
    if user_id not in edit_state:
        return

    text = message.text.strip()

    if " " not in text:
        return await message.reply(
            "❌ format salah\ncontoh:\nNAMA https://t.me/xxxx"
        )

    try:
        name, link = text.rsplit(" ", 1)

        if "t.me/" not in link:
            return await message.reply("❌ link tidak valid")

        idx = edit_state[user_id]["idx"]
        data = await load_partner()

        if idx >= len(data):
            del edit_state[user_id]
            return await message.reply("❌ data tidak ditemukan")

        data[idx] = {
            "name": name,
            "link": link,
            "username": normalize_link(link)
        }

        await save_partner(data)

        del edit_state[user_id]

        await message.reply("✅ updated")

    except Exception as e:
        await message.reply(f"❌ error\n{e}")


# ================= ADD BUTTON TAG =================
@app.on_message(filters.command("addbuttontag") & filters.private)
async def addbuttontag_cmd(client, message):
    user = message.from_user

    if user.id not in OWNER_IDS:
        return await message.reply("❌ Khusus owner")

    if len(message.command) < 2:
        return await message.reply(
            "Format:\n/addbuttontag NAMA - LINK"
        )

    text = message.text.replace("/addbuttontag", "", 1).strip()

    if "-" not in text:
        return await message.reply(
            "Format:\n/addbuttontag NAMA - LINK"
        )

    name, link = text.split("-", 1)
    name = name.strip()
    link = link.strip()

    # 🔥 SIMPAN PER GROUP
    for gc_id in TARGET_CHATS:
        custom_buttons[str(gc_id)] = {
            "name": name,
            "link": link
        }

    await save_buttons(custom_buttons)

    await message.reply(
        f"✅ Button diset ke {len(TARGET_CHATS)} grup\n{name} -> {link}"
    )



