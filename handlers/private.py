import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import *
from utils.helpers import normalize_link
from utils.storage import load_partner, load_limit, get_today_wib
from workers.tagall import task_queue, user_queue, WORKER_ACTIVE


# ================= CEK JOIN =================
async def is_user_joined(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_GROUP, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ================= HANDLER PRIVATE =================
@Client.on_message(filters.private & filters.text)
async def handle_private(client, message):
    global WORKER_ACTIVE

    user_id = message.from_user.id
    text = message.text or ""

    # ================= FORCE JOIN =================
    if not await is_user_joined(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 JOIN GROUP", url=FORCE_LINK)],
            [InlineKeyboardButton("✅ CEK LAGI", callback_data="cek_join")]
        ])

        await message.reply_text(
            "🚫 AKSES DITOLAK\n\n"
            "📢 Wajib join group dulu\n"
            "🔓 Klik CEK LAGI setelah join",
            reply_markup=buttons
        )
        return

    # ================= WORKER OFF =================
    if not WORKER_ACTIVE:
        await message.reply_text("❌ Tagall sedang OFF")
        return

    # ================= VALIDASI TEXT =================
    if not text:
        return

    links = re.findall(r"(https?://t\.me/\S+)", text)

    if not links:
        await message.reply_text("❌ Tidak ada link t.me")
        return

    data = load_partner()

    # ================= VALIDASI PARTNER =================
    valid = any(
        isinstance(p, dict) and (
            normalize_link(l) == p.get("username") or
            l in p.get("link", "")
        )
        for l in links for p in data
    )

    if not valid:
        await message.reply_text("❌ Link tidak terdaftar partner")
        return

    # ================= LIMIT =================
    limit_data = load_limit()
    today = get_today_wib()

    partner_link = links[0]

    partner_key = next(
        (
            p.get("username")
            for p in data
            if partner_link in p.get("link", "")
        ),
        normalize_link(partner_link)
    )

    if limit_data.get(partner_key) == today:
        await message.reply_text("❌ Sudah request hari ini")
        return

    # ================= ANTRIAN =================
    antrian = task_queue.qsize()

    if antrian >= 5:
        await message.reply_text(
            "⚠️ ANTRIAN PENUH\n\n"
            "⏳ Coba lagi nanti"
        )
        return

    # ================= MASUK QUEUE =================
    if user_id not in user_queue:
        user_queue.append(user_id)

    posisi = user_queue.index(user_id) + 1

    if posisi == 1:
        await message.reply_text(
            "📢 Sedang diproses...\n⏳ ±5 menit"
        )
    else:
        await message.reply_text(
            f"⏳ Masuk antrian\nPosisi: {posisi}"
        )

    # ================= MASUK TASK =================
    for chat_id in TARGET_CHATS:
        await task_queue.put((chat_id, text, user_id))
