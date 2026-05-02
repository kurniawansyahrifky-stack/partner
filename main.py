from client import app

from modules.start import start_cmd
from modules.tagall import tagall_cmd, cancel_cmd
from modules.partner_list import list_partner
from modules.owner import *
from modules.owner_panel import *
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


if __name__ == "__main__":
    import asyncio
    from pyrogram import idle
    asyncio.run(main())
