import asyncio
from pyrogram import Client

# ================= CONFIG =================
from config import API_ID, API_HASH, BOT_TOKEN

# ================= IMPORT MODULE =================
from modules.start import start_cmd
from modules.partner_list import *
from modules.tagall import tagall_cmd, cancel_cmd
from modules.button_handler import button_handler
from modules.edit_and_button import handle_edit
from modules.owner import *
from modules.owner_panel import *

# ================= INIT APP =================
app = Client(
    "partner-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= REGISTER HANDLER =================
def register_handlers():

    # COMMAND
    app.add_handler(start_cmd)
    app.add_handler(tagall_cmd)
    app.add_handler(cancel_cmd)

    app.add_handler(add_partner)
    app.add_handler(del_partner)
    app.add_handler(list_partner)

    app.add_handler(owner_panel)

    # CALLBACK
    app.add_handler(button_handler)

    # TEXT (EDIT / PRIVATE)
    app.add_handler(handle_edit)


# ================= MAIN =================
async def main():
    register_handlers()

    await app.start()
    print("🚀 BOT PYROGRAM RUNNING...")

    await idle()


# ================= RUN =================
if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
