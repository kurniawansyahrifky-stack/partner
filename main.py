import asyncio
from pyrogram import idle
from client import app

from modules.start import start_cmd
from modules.tagall import tagall_cmd, cancel_cmd
from modules.partner_list import list_partner
from modules.button_handler import button_handler
from modules.edit_and_button import handle_edit


def register_handlers():
    app.add_handler(start_cmd)
    app.add_handler(tagall_cmd)
    app.add_handler(cancel_cmd)
    app.add_handler(list_partner)
    app.add_handler(button_handler)
    app.add_handler(handle_edit)


async def main():
    register_handlers()
    await app.start()
    print("🚀 BOT RUNNING...")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
