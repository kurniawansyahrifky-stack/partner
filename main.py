import asyncio
from pyrogram import idle
from client import app

import modules.start
import modules.tagall
import modules.partner_list
import modules.button_handler
import modules.edit_and_button


async def main():
    await app.start()
    print("🚀 BOT RUNNING...")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
