import os
import re
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def parse_telegram_link(link: str):
    """টেলিগ্রাম লিংক parse করে"""
    # Public link: t.me/channelname/123
    public_match = re.match(r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)/(\d+)', link)
    if public_match:
        username = public_match.group(1)
        message_id = int(public_match.group(2))
        return username, message_id
    return None, None

def get_file_from_bot_api(channel_username: str, message_id: int):
    """Bot API দিয়ে ফাইল তথ্য আনে"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/forwardMessage"
    
    # Bot নিজের কাছে forward করে file_id নেয়
    resp = requests.post(url, json={
        "chat_id": "@HSNK_Downloaderbot",  # bot এর username
        "from_chat_id": f"@{channel_username}",
        "message_id": message_id
    })
    return resp.json()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 আস্সালামু আলাইকুম!\n\n"
        "🤖 আমি *HSNK Downloader Bot*\n\n"
        "📥 *কিভাবে ব্যবহার করবেন:*\n"
        "Public চ্যানেলের লিংক পাঠান!\n\n"
        "উদাহরণ:\n"
        "`https://t.me/channelname/123`\n\n"
        "⚠️ শুধু Public চ্যানেল সাপোর্ট করে।",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *সাহায্য*\n\n"
        "Public চ্যানেল লিংক এরকম হবে:\n"
        "`https://t.me/channelname/123`\n\n"
        "❓ সমস্যা হলে: @HSNK_TEAM",
        parse_mode="Markdown"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if 't.me/' not in text:
        await update.message.reply_text(
            "❌ এটা টেলিগ্রাম লিংক না!\n\n"
            "সঠিক লিংক:\n"
            "`https://t.me/channelname/123`",
            parse_mode="Markdown"
        )
        return

    # Private link চেক
    if 't.me/c/' in text:
        await update.message.reply_text(
            "⚠️ Private চ্যানেল সাপোর্ট নেই।\n"
            "শুধু Public চ্যানেলের লিংক দিন।"
        )
        return

    processing_msg = await update.message.reply_text("⏳ প্রসেস হচ্ছে...")

    channel, message_id = parse_telegram_link(text)

    if not channel:
        await processing_msg.edit_text("❌ লিংকটি সঠিক নয়!")
        return

    try:
        # Bot API দিয়ে message forward করে ফাইল নাও
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        
        # প্রথমে message info নাও
        get_msg_url = f"{api_url}/forwardMessage"
        chat_id = update.message.chat_id
        
        resp = requests.post(get_msg_url, json={
            "chat_id": chat_id,
            "from_chat_id": f"@{channel}",
            "message_id": message_id
        })
        
        data = resp.json()
        
        if data.get("ok"):
            await processing_msg.edit_text("✅ ফাইল পাঠানো হয়েছে!")
        else:
            error = data.get("description", "অজানা সমস্যা")
            
            if "chat not found" in error.lower():
                await processing_msg.edit_text(
                    "❌ চ্যানেলটি খুঁজে পাওয়া যায়নি!\n\n"
                    "• চ্যানেলটি Public কিনা দেখুন\n"
                    "• লিংকটি সঠিক কিনা দেখুন"
                )
            elif "message to forward not found" in error.lower():
                await processing_msg.edit_text(
                    "❌ মেসেজটি খুঁজে পাওয়া যায়নি!\n"
                    "Message ID সঠিক কিনা দেখুন।"
                )
            elif "bot is not a member" in error.lower() or "forbidden" in error.lower():
                await processing_msg.edit_text(
                    "❌ এই চ্যানেলে Bot এর অ্যাক্সেস নেই!\n\n"
                    "সমাধান:\n"
                    "• চ্যানেলটি Public করুন, অথবা\n"
                    f"• @HSNK_Downloaderbot কে চ্যানেলে Member করুন"
                )
            else:
                await processing_msg.edit_text(
                    f"❌ সমস্যা হয়েছে!\n{error}"
                )

    except Exception as e:
        logger.error(f"Error: {e}")
        await processing_msg.edit_text(
            "❌ সমস্যা হয়েছে! আবার চেষ্টা করুন।"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    print("🤖 HSNK Downloader Bot চালু হয়েছে!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
