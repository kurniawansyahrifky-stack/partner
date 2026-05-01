import asyncio
import random
import html
import re
from collections import deque

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.members import get_members
from bot.utils.limit import load_limit, save_limit, get_today_wib
from bot.utils.helpers import normalize_link

# ================= GLOBAL =================
task_queue = asyncio.Queue()
user_queue = []
progress_map = {}

WORKER_ACTIVE = True

print("QUEUE INIT:", user_queue)


# ================= PROGRESS =================
async def update_progress(client, user_id, current, total):
    percent = int((current / total) * 100) if total else 0
    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)

    try:
        if user_id in progress_map:
            await client.edit_message_text(
                chat_id=user_id,
                message_id=progress_map[user_id],
                text=f"🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐏𝐑𝐎𝐒𝐄𝐒\n\n[{bar}] {percent}%\n👥 {current}/{total}"
            )
    except:
        pass


async def start_progress(client, user_id):
    msg = await client.send_message(
        chat_id=user_id,
        text="🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐃𝐈𝐌𝐔𝐋𝐀𝐈\n\n⏳ 0%"
    )
    progress_map[user_id] = msg.id


# ================= AUTO DELETE =================
async def auto_delete_messages(client, chat_id, message_ids):
    print("🧹 AUTO DELETE START")

    await asyncio.sleep(120)

    for msg_id in message_ids:
        if not msg_id:
            continue
        try:
            await client.delete_messages(chat_id, msg_id)
            print("✔ hapus:", msg_id)
            await asyncio.sleep(0.3)
        except Exception as e:
            print("❌ GAGAL HAPUS:", msg_id, e)

    print("✅ AUTO DELETE SELESAI")


# ================= WORKER =================
async def tagall_worker(client):
    print("🔥 WORKER HIDUP (PYROGRAM)")

    while True:
        chat_id, text, user_id = await task_queue.get()

        # ================= WORKER OFF =================
        if not WORKER_ACTIVE:
            try:
                await client.send_message(user_id, "❌ Maaf lagi close tagall dulu")
            except:
                pass

            task_queue.task_done()
            continue

        # ================= LIMIT =================
        limit_data = await load_limit()
        today = get_today_wib()

        links = re.findall(r"(https?://t\.me/\S+)", text)
        partner_link = links[0] if links else "-"
        partner_key = normalize_link(partner_link)

        if limit_data.get(partner_key) == today:
            task_queue.task_done()
            continue

        print("🔥 AMBIL TASK:", user_id)

        try:
            # ================= ANTRIAN =================
            if user_queue and user_queue[0] != user_id:
                await asyncio.sleep(0.3)
                task_queue.task_done()
                continue

            print("🚀 PROSES USER:", user_id)

            start_msg = (
                "🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐃𝐈𝐌𝐔𝐋𝐀𝐈\n\n"
                f"🔗 partner : {partner_link}\n"
                "⏰ durasi : 5 menit\n"
                "📍 JIKA BOT EROR SILAHKAN KESINI @tagallnoirfluerBot"
            )

            keyboard_start = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 My Store", url="https://t.me/storegarf")]
            ])

            await client.send_message(chat_id, start_msg)
            await client.send_message(user_id, start_msg, reply_markup=keyboard_start)

            # ================= START =================
            await start_progress(client, user_id)

            sent_messages = []
            sent = 0

            members = await get_members(client, chat_id)
            if not members:
                task_queue.task_done()
                continue

            user_ids = list(members.keys())
            total = len(user_ids)

            random.shuffle(user_ids)

            BATCH_SIZE = 4
            BASE_DELAY = 1.4

            start_time = asyncio.get_event_loop().time()
            duration = 300

            last_success_time = asyncio.get_event_loop().time()

            # ================= LOOP =================
            while asyncio.get_event_loop().time() - start_time < duration:

                if asyncio.get_event_loop().time() - last_success_time > 15:
                    print("⚠️ STUCK DETECTED")
                    break

                for i in range(0, total, BATCH_SIZE):
                    if asyncio.get_event_loop().time() - start_time >= duration:
                        break

                    batch = user_ids[i:i + BATCH_SIZE]

                    mention_text = ""
                    for uid in batch:
                        name = html.escape(members[uid])
                        mention_text += f'<a href="tg://user?id={uid}">{name}</a> '

                    retry = 0

                    while retry < 3:
                        try:
                            msg = await client.send_message(
                                chat_id,
                                f"💕 𝑩𝑶𝑻 𝑻𝑨𝑮𝑨𝑳𝑳 𝗡𝗢𝗜𝗥𝗙𝗟𝗨𝗘𝗥 💖\n\n{text}\n\n{mention_text}",
                                parse_mode="HTML"
                            )

                            sent_messages.append(msg.id)

                            sent += len(batch)
                            await update_progress(client, user_id, sent, total)

                            last_success_time = asyncio.get_event_loop().time()

                            print(f"📊 PROGRESS: {sent}/{total}")
                            break

                        except Exception as e:
                            print("❌", e)
                            retry += 1

                            if "Retry in" in str(e):
                                try:
                                    wait = int(re.search(r"Retry in (\d+)", str(e)).group(1))
                                    print(f"⏳ RETRY WAIT: {wait}s")
                                    await asyncio.sleep(wait + 1)
                                except:
                                    await asyncio.sleep(3)

                            elif "Too Many Requests" in str(e):
                                print("🚫 FLOOD")
                                await asyncio.sleep(3 + retry)

                            elif "Timed out" in str(e):
                                print("⌛ TIMEOUT")
                                await asyncio.sleep(2 + retry)

                            else:
                                await asyncio.sleep(1 + retry)

                    await asyncio.sleep(BASE_DELAY + random.uniform(0.15, 0.35))

            # ================= DONE =================
            keyboard_done = InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 Creator", url="https://t.me/Brsik23")]
            ])

            await client.send_message(
                chat_id,
                f"✅ 𝐓𝐀𝐆𝐀𝐋𝐋 𝐒𝐄𝐋𝐄𝐒𝐀𝐈\n\n"
                f"🔗 partner : {partner_link}\n"
                f"👥 Total: {sent}",
                reply_markup=keyboard_done
            )

            # SAVE LIMIT
            limit_data[partner_key] = today
            await save_limit(limit_data)

            # AUTO DELETE
            if sent_messages:
                asyncio.create_task(
                    auto_delete_messages(client, chat_id, sent_messages.copy())
                )

            # PRIVATE DONE
            try:
                if user_id in progress_map:
                    await client.edit_message_text(
                        chat_id=user_id,
                        message_id=progress_map[user_id],
                        text=f"✅ 𝐓𝐀𝐆𝐀𝐋𝐋 𝐒𝐄𝐋𝐀𝐈\n\n"
                             f"🔗 partner : {partner_link}\n"
                             f"🧹 auto delete aktif\n"
                             f"👥 Total: {sent}\n"
                             f"⏱ 5 menit"
                    )
            except Exception as e:
                print("❌ edit private:", e)

        except Exception as e:
            print("❌ ERROR:", e)

        finally:
            if user_queue:
                if user_queue[0] == user_id:
                    user_queue.pop(0)
                elif user_id in user_queue:
                    user_queue.remove(user_id)

            task_queue.task_done()
