import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Required channel usernames
REQUIRED_CHANNELS = ["@the_traitors_s1", "@web_series_devil"]

# Load episode data from JSON
with open("episodes.json", "r") as f:
    EPISODE_DATA = json.load(f)

# Store user requests temporarily
user_requests = {}

# Check if user is in all required channels
async def is_user_subscribed(user_id, context):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id

    if not args:
        await update.message.reply_text("❗ Invalid access. Please click a valid episode button from the channel.")
        return

    episode_quality = args[0]  # e.g., 'ep1_720p'
    user_requests[user_id] = episode_quality

    if await is_user_subscribed(user_id, context):
        await send_video(user_id, context)
    else:
        # Ask user to join channels
        buttons = [[InlineKeyboardButton(f"🔗 Join {channel}", url=f"https://t.me/{channel[1:]}")] for channel in REQUIRED_CHANNELS]
        buttons.append([InlineKeyboardButton("✅ I’ve Joined", callback_data="check_join")])
        await update.message.reply_text(
            "🔒 Please join all the channels below to unlock this content:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Enhanced callback when "I've Joined" is clicked
async def join_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    updated_buttons = []
    all_joined = True

    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                updated_buttons.append([InlineKeyboardButton(f"✅ Joined {channel}", url=f"https://t.me/{channel[1:]}")])
            else:
                updated_buttons.append([InlineKeyboardButton(f"🔗 Join {channel}", url=f"https://t.me/{channel[1:]}")])
                all_joined = False
        except:
            updated_buttons.append([InlineKeyboardButton(f"🔗 Join {channel}", url=f"https://t.me/{channel[1:]}")])
            all_joined = False

    # Re-add the "I’ve Joined" button
    updated_buttons.append([InlineKeyboardButton("✅ I’ve Joined", callback_data="check_join")])

    if all_joined:
        try:
            # Delete the join prompt message
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except Exception as e:
            print(f"Failed to delete message: {e}")

        await send_video(user_id, context)

    else:
        await query.edit_message_text(
            "🔒 You still need to join all required channels to unlock this content:",
            reply_markup=InlineKeyboardMarkup(updated_buttons)
        )

# Function to send the correct video
async def send_video(user_id, context):
    payload = user_requests.get(user_id)
    if not payload:
        return

    try:
        episode_label, quality = payload.split("_")
        episode_title = f"Episode {episode_label.replace('ep', '')}"
        file_id = EPISODE_DATA[episode_title][quality]
        await context.bot.send_video(chat_id=user_id, video=file_id, caption=f"🎬 {episode_title} [{quality}]")
    except Exception as e:
        print(f"Error sending video: {e}")
        await context.bot.send_message(chat_id=user_id, text="⚠️ Could not find the requested video.")

# Main entry
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(join_check_callback, pattern="check_join"))
    print("🤖 Bot running...")
    app.run_polling()
