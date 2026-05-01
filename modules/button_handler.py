from pyrogram import filters
from pyrogram.errors import FloodWait

from bot.client import app
from config import OWNER_IDS

from bot.utils.files import load_setting, save_setting, load_partner
from bot.utils.state import stop_flag, manual_setup, manual_messages
from bot.modules.tagall_worker import handle_durasi

import asyncio


WORKER_ACTIVE = True


# ================= CALLBACK HANDLER =================
@app.on_callback_query()
async def button_handler(client, query):
    global WORKER_ACTIVE

    chat_id = query.message.chat.id
    user_id = query.from_user.id
    data_btn = query.data

    try:
        await query.answer()
    except:
        pass

    data = await load_setting()

    # ================= RULES =================
    if data_btn == "rules":
        return await query.message.reply(
            data.get("rules", "tidak ada rules")
        )

    # ================= STOP TAGALL =================
    if data_btn == "manual_stop":

        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in ("administrator", "creator"):
                return await query.answer("❌ Khusus admin", show_alert=True)
        except:
            return

        stop_flag[chat_id] = True
        manual_setup.pop(chat_id, None)

        return await query.message.reply("⛔ Tagall dihentikan")

    # ================= CLEAR CHAT =================
    if data_btn == "manual_clear":

        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in ("administrator", "creator"):
                return await query.answer("❌ Khusus admin", show_alert=True)
        except:
            return

        msgs = manual_messages.get(chat_id, [])

        for msg_id in msgs:
            try:
                await client.delete_messages(chat_id, msg_id)
            except:
                pass

        manual_messages[chat_id] = []

        return await query.message.reply("🧹 Chat dibersihkan")

    # ================= DURASI =================
    if data_btn.startswith("dur_"):
        return await handle_durasi(client, query)

    # ================= AUTOTAG =================
    if data_btn == "cmd_autotag":
        return await client.send_message(
            user_id,
            "🤖 AUTO TAG\n\nGunakan:\n/autotag pesan"
        )

    # ================= OWNER ONLY =================
    if user_id not in OWNER_IDS:
        return

    # ================= OWNER MENU =================

    if data_btn == "cmd_addpict":
        return await client.send_message(
            user_id,
            "🖼️ Reply foto lalu /addpict"
        )

    if data_btn == "cmd_delpict":
        if "start_pict" not in data:
            return await client.send_message(user_id, "⚠️ Foto belum ada")

        data.pop("start_pict", None)
        await save_setting(data)

        return await client.send_message(user_id, "✅ Foto dihapus")

    if data_btn == "cmd_addpj":
        return await client.send_message(
            user_id,
            "👤 /addpj @username"
        )

    if data_btn == "cmd_delpj":
        if "pj" not in data:
            return await client.send_message(user_id, "⚠️ PJ belum ada")

        data.pop("pj", None)
        await save_setting(data)

        return await client.send_message(user_id, "✅ PJ dihapus")

    if data_btn == "cmd_listpartner":
        partners = await load_partner()

        if not partners:
            return await client.send_message(user_id, "❌ Partner kosong")

        text = "📋 LIST PARTNER\n\n"

        for i, p in enumerate(partners, 1):
            text += f"{i}. {p['name']}\n{p['link']}\n\n"

        return await client.send_message(user_id, text)

    if data_btn == "cmd_on":
        WORKER_ACTIVE = True
        return await client.send_message(user_id, "🟢 Tagall ON")

    if data_btn == "cmd_off":
        WORKER_ACTIVE = False
        return await client.send_message(user_id, "🔴 Tagall OFF")

    if data_btn == "cmd_bc":
        return await client.send_message(
            user_id,
            "📢 Gunakan /bc pesan"
        )
