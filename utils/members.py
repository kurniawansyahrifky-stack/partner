import asyncio


# ================= GET MEMBERS =================
async def get_members(client, chat_id):
    users = {}

    try:
        async for member in client.get_chat_members(chat_id):
            if member.user and not member.user.is_bot:
                name = member.user.first_name or "User"
                users[str(member.user.id)] = name

    except Exception as e:
        print("❌ get_members error:", e)

    return users
