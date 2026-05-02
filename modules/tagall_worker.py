import asyncio
import random
import time
import html

from collections import deque
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from main import app
from utils.state import (
    manual_setup, stop_flag, manual_messages,
    custom_buttons, last_activity
)
from utils.helpers import fancy_name


# ================= CALLBACK DURASI =================
@app.on_callback_query(filters.regex(r"^dur_(.+)$"))
async def handle_durasi(client, query):
    chat_id = query.message.chat.id

    await query.answer()

    if chat_id not in manual_setup:
        return await query.edit_message_text("❌ Session hilang")

    data = query.matches[0].group(1)

    durasi_map = {
        "2": 120,
        "5": 300,
        "10": 600,
        "30": 1800,
        "60": 3600,
        "unli": None
    }

    duration = durasi_map.get(data)

    setup = manual_setup[chat_id]
    msg = setup["msg"]

    await query.edit_message_text("🚀 Tagall manual dimulai...")

    asyncio.create_task(
        run_tagall_manual(client, chat_id, msg, duration)
    )


# ================= TAGALL WORKER =================
async def run_tagall_manual(client, chat_id, msg, duration):
    stop_flag[chat_id] = False
    manual_messages[chat_id] = []

    members = {}

    try:
        async for m in client.get_chat_members(chat_id):
            if m.user:
                members[m.user.id] = m.user.first_name
    except Exception as e:
        print("GET MEMBERS ERROR:", e)
        return

    if not members:
        return

    user_ids = list(members.keys())
    random.shuffle(user_ids)
    queue = deque(user_ids)

    BATCH_SIZE = 3
    current_delay = 2.5

    start_time = time.time()
    sent = 0
    stopped = False

    btn = custom_buttons.get(str(chat_id))

    # ================= LOOP =================
    while queue:

        if stop_flag.get(chat_id):
            stopped = True
            break

        if duration and time.time() - start_time > duration:
            break

        batch = [queue.popleft() for _ in range(min(BATCH_SIZE, len(queue)))]

        mention_list = []
        for uid in batch:
            name = html.escape(members.get(uid, "user"))
            fancy = fancy_name(name)
            mention_list.append(f'<a href="tg://user?id={uid}">{fancy}</a>')

        mention_text = " ".join(mention_list)

        final_text = f"✦ {msg.upper()} ✦\n\n{mention_text}\n\n✦🌑✦"

        keyboard = None
        if btn:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn["name"], url=btn["link"])]
            ])

        try:
            # ❌ FIX: parse_mode DIHAPUS
            sent_msg = await client.send_message(
                chat_id,
                final_text,
                reply_markup=keyboard
            )

            manual_messages[chat_id].append(sent_msg.id)
            sent += len(batch)
            last_activity[chat_id] = time.time()

            await asyncio.sleep(current_delay + random.uniform(0.5, 1.5))

        except FloodWait as e:
            print(f"⚠️ FLOOD → WAIT {e.value}s")

            for uid in reversed(batch):
                queue.appendleft(uid)

            await asyncio.sleep(e.value + random.uniform(1, 3))
            current_delay += 1

        except Exception as e:
            print("SEND ERROR:", e)
            await asyncio.sleep(2)

        if sent > 50:
            current_delay = 3.5
        if sent > 200:
            current_delay = 5
        if sent > 500:
            current_delay = 6

    # ================= DONE =================
    text_done = (
        "⛔ Tagall dihentikan"
        if stopped else
        f"✅ Tagall selesai\n👥 Total tag: {sent}"
    )

    keyboard_clear = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧹 CLEAR CHAT", callback_data="manual_clear")]
    ])

    done_msg = await client.send_message(
        chat_id,
        text_done,
        reply_markup=keyboard_clear
    )

    # ================= AUTO CLEAR =================
    async def auto_clear():
        await asyncio.sleep(120)

        for msg_id in manual_messages.get(chat_id, []):
            try:
                await client.delete_messages(chat_id, msg_id)
            except:
                pass

        try:
            await client.delete_messages(chat_id, done_msg.id)
        except:
            pass

        manual_messages[chat_id] = []

    asyncio.create_task(auto_clear())


# ================= CLEAR BUTTON =================
@app.on_callback_query(filters.regex(r"^manual_clear$"))
async def button_handler(client, query):
    chat_id = query.message.chat.id

    await query.answer()

    msgs = manual_messages.get(chat_id, [])

    for msg_id in msgs:
        try:
            await client.delete_messages(chat_id, msg_id)
        except:
            pass

    try:
        await query.message.delete()
    except:
        pass

    manual_messages[chat_id] = []
