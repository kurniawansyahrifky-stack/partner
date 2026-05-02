from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from client import app
from config import OWNER_IDS
from utils.files import load_partner

PAGE_SIZE = 10


# ================= COMMAND =================
@app.on_message(filters.command("listpartner") & filters.user(OWNER_IDS))
async def list_partner(client, message):
    await send_partner_page_message(message, 0)


# ================= SEND (COMMAND) =================
async def send_partner_page_message(message, page: int):
    data = await load_partner()

    if not data:
        return await message.reply("❌ kosong")

    total = len(data)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = f"📋 LIST PARTNER\nHalaman {page+1}\n\n"

    for i, p in enumerate(data[start:end], start + 1):
        text += f"{i}. {p.get('name','-')}\n{p.get('link','-')}\n\n"

    keyboard = build_buttons(page, total)

    await message.reply(text, reply_markup=keyboard)


# ================= SEND (CALLBACK) =================
async def send_partner_page_callback(query, page: int):
    data = await load_partner()

    if not data:
        return await query.edit_message_text("❌ kosong")

    total = len(data)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = f"📋 LIST PARTNER\nHalaman {page+1}\n\n"

    for i, p in enumerate(data[start:end], start + 1):
        text += f"{i}. {p.get('name','-')}\n{p.get('link','-')}\n\n"

    buttons = build_buttons(page, total)

    await query.edit_message_text(text, reply_markup=buttons)


# ================= BUTTON BUILDER =================
def build_buttons(page, total):
    buttons = []

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    # EDIT BUTTON (2 KOLOM)
    row = []
    for i in range(start, min(end, total)):
        row.append(
            InlineKeyboardButton(
                f"✏️ {i+1}",
                callback_data=f"edit_menu_{i}"
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # NAVIGATION
    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton("⬅️ Prev", callback_data=f"partner_{page-1}")
        )

    if end < total:
        nav.append(
            InlineKeyboardButton("➡️ Next", callback_data=f"partner_{page+1}")
        )

    if nav:
        buttons.append(nav)

    # CLOSE
    buttons.append([
        InlineKeyboardButton("❌ Close", callback_data="partner_close")
    ])

    return InlineKeyboardMarkup(buttons)


# ================= CALLBACK HANDLER =================
@app.on_callback_query(filters.regex(r"^partner_(\d+)$"))
async def partner_page_cb(client, query):
    page = int(query.matches[0].group(1))
    await send_partner_page_callback(query, page)


@app.on_callback_query(filters.regex(r"^partner_close$"))
async def partner_close_cb(client, query):
    await query.message.delete()
