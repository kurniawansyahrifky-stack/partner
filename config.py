import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/get")

TARGET_CHATS = [-1002896045673]
FORCE_GROUP = -1002896045673
FORCE_LINK = "https://t.me/ofcnoirfleur"

OWNER_IDS = [8209644174, 5744453710]

PARTNER_FILE = "partner.json"
SETTING_FILE = "setting.json"
QUEUE_FILE = "queue.json"
AUTO_TAG_FILE = "autotag.json"
BUTTON_FILE = "buttons.json"

BACKUP_DIR = "backups"
SERVICE_NAME = "noirbot"
