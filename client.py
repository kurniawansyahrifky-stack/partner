import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# ================= LOG =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("PARTNER-BOT")

# ================= APP =================
app = Client(
    "partner_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

