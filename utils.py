import json

async def check_channel_joined(user_id, bot, channel_username):
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def get_episodes():
    with open("episodes.json", "r") as f:
        return json.load(f)
