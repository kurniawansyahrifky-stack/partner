from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot.client import app
from config import OWNER_IDS

from bot.utils.files import load_setting, save_setting

import asyncio


WORKER_ACTIVE = True


# ================= ON / OFF =================
@app.on_message(filters.command("on") & filters.private & filters.user(OWNER_IDS))
async def bot_on(client, message):
    global WORKER_ACTIVE
    WORKER_ACTIVE = True
    await message.reply("✅ Tagall dibuka (ON)")


@app.on_message(filters.command("off") & filters.private & filters.user(OWNER_IDS))
async def bot_off(client, message):
    global WORKER_ACTIVE
    WORKER_ACTIVE = False
    await message.reply("❌ Tagall dimatikan (OFF)")


# ================= HELP OWNER =================
@app.on_message(filters.command("owner") & filters.private & filters.user(OWNER_IDS))
async def help_owner(client, message):

    text = (
        "👑 𝗢𝗪𝗡𝗘𝗥 𝗣𝗔𝗡𝗘𝗟\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📋 /listpartner\n"
        "📢 /bc pesan\n"
        "🏷️ /tagall pesan\n"
        "⚙️ /on /off\n"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Partner", callback_data="cmd_listpartner")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="cmd_bc")
        ],
        [
            InlineKeyboardButton("🏷️ Tagall", callback_data="cmd_tagall")
        ],
        [
            InlineKeyboardButton("🟢 ON", callback_data="cmd_on"),
            InlineKeyboardButton("🔴 OFF", callback_data="cmd_off")
        ]
    ])

    await message.reply(text, reply_markup=keyboard)


# ================= MEDIA =================
@app.on_message(filters.command("addpict") & filters.private & filters.user(OWNER_IDS))
async def add_pict(client, message):

    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("❌ reply foto dengan /addpict")

    file_id = message.reply_to_message.photo[-1].file_id

    data = await load_setting()
    data["start_pict"] = file_id
    await save_setting(data)

    await message.reply("✅ foto disimpan")


@app.on_message(filters.command("delpict") & filters.private & filters.user(OWNER_IDS))
async def del_pict(client, message):
    data = await load_setting()
    data.pop("start_pict", None)
    await save_setting(data)

    await message.reply("✅ foto dihapus")


# ================= PJ =================
@app.on_message(filters.command("addpj") & filters.private & filters.user(OWNER_IDS))
async def add_pj(client, message):

    if len(message.command) < 2:
        return await message.reply("❌ /addpj username")

    username = message.command[1].replace("@", "")

    data = await load_setting()
    data["pj"] = username
    await save_setting(data)

    await message.reply("✅ PJ disimpan")


@app.on_message(filters.command("delpj") & filters.private & filters.user(OWNER_IDS))
async def del_pj(client, message):
    data = await load_setting()
    data.pop("pj", None)
    await save_setting(data)

    await message.reply("✅ PJ dihapus")


# ================= RULES =================
@app.on_message(filters.command("addrules") & filters.private & filters.user(OWNER_IDS))
async def add_rules(client, message):

    text = (
        message.reply_to_message.text
        if message.reply_to_message
        else " ".join(message.command[1:])
    )

    if not text:
        return await message.reply("❌ isi rules")

    data = await load_setting()
    data["rules"] = text
    await save_setting(data)

    await message.reply("✅ rules disimpan")


@app.on_message(filters.command("delrules") & filters.private & filters.user(OWNER_IDS))
async def del_rules(client, message):
    data = await load_setting()
    data.pop("rules", None)
    await save_setting(data)

    await message.reply("✅ rules dihapus")


# ================= BROADCAST =================
@app.on_message(filters.command("bc") & filters.user(OWNER_IDS))
async def bc_cmd(client, message):

    data = await load_setting()
    users = data.get("users", [])

    if not users:
        return await message.reply("❌ Tidak ada user")

    await message.reply("🚀 Broadcast dimulai...")

    success = 0
    failed = 0

    for user_id in users:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(user_id)

            elif len(message.command) > 1:
                text = " ".join(message.command[1:])
                await client.send_message(user_id, text)

            else:
                continue

            success += 1
            await asyncio.sleep(1.5)  # 🔥 delay aman

        except FloodWait as e:
            await asyncio.sleep(e.value)

        except:
            failed += 1

    await message.reply(
        f"📢 Broadcast selesai\n\n✅ {success}\n❌ {failed}"
    )
