from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.client import app
from bot.utils.state import manual_setup, stop_flag, auto_data
from bot.utils.files import save_autotag


# ================= TAGALL =================
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    chat = message.chat
    user = message.from_user

    # 🔥 CEK ADMIN
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status not in ("administrator", "creator"):
            return await message.reply("❌ Khusus admin")
    except:
        return

    # 🔥 SIMPAN LAST GROUP (AUTO TAG)
    user_id = str(user.id)

    if user_id not in auto_data:
        auto_data[user_id] = {}

    auto_data[user_id]["chat_id"] = chat.id
    await save_autotag(auto_data)

    # ================= INPUT =================
    text = " ".join(message.command[1:])

    if text:
        manual_setup[chat.id] = {"msg": text, "mode": "text"}
    elif message.reply_to_message:
        manual_setup[chat.id] = {
            "msg": message.reply_to_message.id,
            "mode": "reply"
        }
    else:
        return await message.reply("❌ Isi teks atau reply pesan")

    # ================= BUTTON =================
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("2 menit", callback_data="dur_2"),
            InlineKeyboardButton("5 menit", callback_data="dur_5")
        ],
        [
            InlineKeyboardButton("10 menit", callback_data="dur_10"),
            InlineKeyboardButton("30 menit", callback_data="dur_30")
        ],
        [
            InlineKeyboardButton("60 menit", callback_data="dur_60"),
            InlineKeyboardButton("Unlimited", callback_data="dur_unli")
        ]
    ])

    await message.reply(
        "⏱ Pilih durasi:",
        reply_markup=keyboard
    )


# ================= CANCEL =================
@app.on_message(filters.command("cancel") & filters.group)
async def cancel_cmd(client, message):
    chat = message.chat
    user = message.from_user

    # 🔥 CEK ADMIN
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status not in ("administrator", "creator"):
            return await message.reply("❌ Khusus admin")
    except:
        return

    # 🔥 STOP FLAG
    stop_flag[chat.id] = True

    try:
        await message.reply("⛔ Tagall dihentikan")
    except:
        pass
