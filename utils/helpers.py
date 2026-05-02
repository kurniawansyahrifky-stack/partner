import re
import time

def fancy_name(name: str):
    return name.strip().title()

# ================= LINK =================
def normalize_link(link: str) -> str:
    if not link:
        return ""
    link = link.strip()
    link = link.replace("https://", "").replace("http://", "")
    link = link.replace("t.me/", "")
    return link.lower()


# ================= GET GROUP NAME =================
async def get_group_name(client, link: str) -> str:
    username = normalize_link(link)

    if not username:
        return "Unknown Group"

    try:
        chat = await client.get_chat(username)
        return chat.title or "Unknown Group"
    except Exception as e:
        print("❌ get_group_name error:", e)
        return "Unknown Group"


# ================= FORMAT =================
def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def mention_user(user) -> str:
    name = user.first_name or "User"
    return f"<a href='tg://user?id={user.id}'>{escape_html(name)}</a>"


# ================= VALIDATION =================
def is_valid_username(username: str) -> bool:
    if not username:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_]{5,32}$", username))


def is_group(chat_id: int) -> bool:
    return str(chat_id).startswith("-100")


# ================= RATE LIMIT =================
def is_rate_limited(user_id: int, rate_limit: dict, cooldown: int = 5) -> bool:
    now = time.time()

    if user_id in rate_limit:
        if now - rate_limit[user_id] < cooldown:
            return True

    rate_limit[user_id] = now
    return False


# ================= TEXT CLEAN =================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ================= CHUNK =================
def chunk_list(data, size: int):
    for i in range(0, len(data), size):
        yield data[i:i + size]
