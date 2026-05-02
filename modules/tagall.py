from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus

from client import app
from utils.state import manual_setup, stop_flag, auto_data
from utils.files import save_autotag


# ================= TAGALL =================
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    chat = message.chat

    # 🔥 VALIDASI USER
    if not message.from_user:
        return await message.reply("❌ Tidak bisa dipakai (anonymous / channel sender)")

    user = message.from_user

    # 🔥 CEK ADMIN (FIXED ENUM)
    try:
        member = await client.get_chat_member(chat.id, user.id)

        print("DEBUG STATUS:", member.status)

        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ):
            return await message.reply(
                f"❌ Khusus admin group\nSTATUS: {member.status}"
            )

    except Exception as e:
        return await message.reply(f"⚠️ ERROR CEK ADMIN:\n{e}")

    # 🔥 SAVE LAST GROUP
    user_id = str(user.id)

    if user_id not in auto_data:
        auto_data[user_id] = {}

    auto_data[user_id]["chat_id"] = chat.id
    await save_autotag(auto_data)

    # ================= INPUT =================
    text = " ".join(message.command[1:])

    if text:
        manual_setup[chat.id] = {
            "msg": text,
            "mode": "text"
        }

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

    await message.reply("⏱ Pilih durasi:", reply_markup=keyboard)


# ================= CANCEL =================
@app.on_message(filters.command("cancel") & filters.group)
async def cancel_cmd(client, message):
    chat = message.chat

    if not message.from_user:
        return await message.reply("❌ Tidak valid user")

    user = message.from_user

    try:
        member = await client.get_chat_member(chat.id, user.id)

        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ):
            return await message.reply("❌ Khusus admin group")

    except Exception as e:
        return await message.reply(f"⚠️ ERROR CEK ADMIN:\n{e}")

    stop_flag[chat.id] = True
    await message.reply("⛔ Tagall dihentikan")
