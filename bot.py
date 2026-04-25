import os
import re
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# আপনার তথ্য এখানে বসান
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", "32368909"))
API_HASH = os.environ.get("API_HASH", "70266fe896edd5623f1beb74adcf4cab")
# ============================================================

# Telethon client (MTProto - private channel access)
telethon_client = TelegramClient('hsnk_session', API_ID, API_HASH)

def parse_telegram_link(link: str):
    """টেলিগ্রাম লিংক parse করে channel ও message id বের করে"""
    
    # Private link: t.me/c/1234567890/123
    private_match = re.match(r'(?:https?://)?t\.me/c/(\d+)/(\d+)', link)
    if private_match:
        channel_id = int("-100" + private_match.group(1))
        message_id = int(private_match.group(2))
        return channel_id, message_id, "private"
    
    # Public link: t.me/channelname/123
    public_match = re.match(r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)/(\d+)', link)
    if public_match:
        channel_username = public_match.group(1)
        message_id = int(public_match.group(2))
        return channel_username, message_id, "public"
    
    return None, None, None

def get_file_info(message):
    """মেসেজ থেকে ফাইলের তথ্য বের করে"""
    if not message.media:
        return None, None, None
    
    if isinstance(message.media, MessageMediaPhoto):
        return "📷 Photo", "photo.jpg", "image/jpeg"
    
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        file_name = "file"
        mime_type = doc.mime_type or "application/octet-stream"
        
        for attr in doc.attributes:
            if hasattr(attr, 'file_name') and attr.file_name:
                file_name = attr.file_name
                break
            elif hasattr(attr, 'title') and attr.title:
                file_name = attr.title
        
        # ফাইল টাইপ অনুযায়ী emoji
        if 'video' in mime_type:
            emoji = "🎬 Video"
        elif 'audio' in mime_type:
            emoji = "🎵 Audio"
        elif 'image' in mime_type:
            emoji = "🖼️ Image"
        elif 'pdf' in mime_type:
            emoji = "📄 PDF"
        elif 'zip' in mime_type or 'rar' in mime_type:
            emoji = "🗜️ Archive"
        else:
            emoji = "📁 File"
        
        size = doc.size
        if size > 1024 * 1024 * 1024:
            size_str = f"{size / (1024**3):.2f} GB"
        elif size > 1024 * 1024:
            size_str = f"{size / (1024**2):.2f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size} bytes"
        
        return emoji, file_name, size_str
    
    return None, None, None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot শুরু করার কমান্ড"""
    await update.message.reply_text(
        "👋 আস্সালামু আলাইকুম!\n\n"
        "🤖 আমি **HSNK Downloader Bot**\n\n"
        "📥 আমি যা করতে পারি:\n"
        "• Public চ্যানেলের ফাইল ডাউনলোড\n"
        "• Private চ্যানেলের ফাইল ডাউনলোড\n"
        "• Video, Photo, Document সব ধরনের ফাইল\n\n"
        "📌 **কিভাবে ব্যবহার করবেন:**\n"
        "শুধু টেলিগ্রাম লিংক পাঠান!\n\n"
        "উদাহরণ:\n"
        "`t.me/channelname/123`\n"
        "`t.me/c/1234567890/456`\n\n"
        "💡 লিংক পাঠালেই ফাইল পাঠিয়ে দেবো!",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help কমান্ড"""
    await update.message.reply_text(
        "📖 **সাহায্য**\n\n"
        "**Public চ্যানেল লিংক:**\n"
        "`https://t.me/channelname/123`\n\n"
        "**Private চ্যানেল লিংক:**\n"
        "`https://t.me/c/1234567890/456`\n\n"
        "⚠️ Private চ্যানেলের ফাইল পেতে হলে\n"
        "আপনাকে সেই চ্যানেলের Member হতে হবে!\n\n"
        "❓ সমস্যা হলে: @HSNK_TEAM",
        parse_mode="Markdown"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """টেলিগ্রাম লিংক হ্যান্ডেল করে"""
    text = update.message.text.strip()
    
    # টেলিগ্রাম লিংক কিনা চেক করো
    if 't.me/' not in text:
        await update.message.reply_text(
            "❌ এটা টেলিগ্রাম লিংক না!\n\n"
            "সঠিক লিংক পাঠান:\n"
            "`t.me/channelname/123`\n"
            "`t.me/c/1234567890/456`",
            parse_mode="Markdown"
        )
        return
    
    # Processing মেসেজ পাঠাও
    processing_msg = await update.message.reply_text(
        "⏳ লিংক প্রসেস হচ্ছে... একটু অপেক্ষা করুন"
    )
    
    channel, message_id, link_type = parse_telegram_link(text)
    
    if not channel:
        await processing_msg.edit_text(
            "❌ লিংকটি সঠিক নয়!\n\n"
            "সঠিক লিংক এরকম হবে:\n"
            "`t.me/channelname/123`"
        )
        return
    
    try:
        # Telethon দিয়ে মেসেজ fetch করো
        async with telethon_client:
            message = await telethon_client.get_messages(channel, ids=message_id)
        
        if not message:
            await processing_msg.edit_text(
                "❌ মেসেজটি খুঁজে পাওয়া যায়নি!\n"
                "লিংকটি সঠিক কিনা দেখুন।"
            )
            return
        
        if not message.media:
            # Text মেসেজ হলে
            msg_text = message.text or message.message or ""
            await processing_msg.edit_text(
                f"ℹ️ এই মেসেজে কোনো ফাইল নেই।\n\n"
                f"📝 মেসেজের টেক্সট:\n{msg_text[:500]}"
            )
            return
        
        # ফাইলের তথ্য বের করো
        file_emoji, file_name, file_size = get_file_info(message)
        
        await processing_msg.edit_text(
            f"✅ ফাইল পাওয়া গেছে!\n\n"
            f"{file_emoji}\n"
            f"📂 নাম: `{file_name}`\n"
            f"💾 সাইজ: {file_size}\n\n"
            f"⬇️ ডাউনলোড হচ্ছে... একটু সময় লাগবে",
            parse_mode="Markdown"
        )
        
        # ফাইল ডাউনলোড করে পাঠাও
        async with telethon_client:
            file_path = await telethon_client.download_media(
                message, 
                file=f"/tmp/{file_name}"
            )
        
        if file_path:
            # Bot দিয়ে ফাইল পাঠাও
            app = context.application
            
            with open(file_path, 'rb') as f:
                if 'Photo' in file_emoji or 'Image' in file_emoji:
                    await context.bot.send_photo(
                        chat_id=update.message.chat_id,
                        photo=f,
                        caption=f"✅ ডাউনলোড সম্পন্ন!\n📂 {file_name}"
                    )
                elif 'Video' in file_emoji:
                    await context.bot.send_video(
                        chat_id=update.message.chat_id,
                        video=f,
                        caption=f"✅ ডাউনলোড সম্পন্ন!\n🎬 {file_name}"
                    )
                elif 'Audio' in file_emoji:
                    await context.bot.send_audio(
                        chat_id=update.message.chat_id,
                        audio=f,
                        caption=f"✅ ডাউনলোড সম্পন্ন!\n🎵 {file_name}"
                    )
                else:
                    await context.bot.send_document(
                        chat_id=update.message.chat_id,
                        document=f,
                        caption=f"✅ ডাউনলোড সম্পন্ন!\n📁 {file_name}"
                    )
            
            # Temp ফাইল মুছে দাও
            os.remove(file_path)
            await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        error_msg = str(e)
        
        if "private" in error_msg.lower() or "forbidden" in error_msg.lower():
            await processing_msg.edit_text(
                "❌ এই চ্যানেলে অ্যাক্সেস নেই!\n\n"
                "Private চ্যানেলের ফাইল পেতে:\n"
                "• আপনাকে সেই চ্যানেলের Member হতে হবে\n"
                "• Bot কে সেই চ্যানেলে Add করতে হবে"
            )
        elif "flood" in error_msg.lower():
            await processing_msg.edit_text(
                "⏰ একটু বেশি রিকোয়েস্ট হয়ে গেছে!\n"
                "কিছুক্ষণ পরে আবার চেষ্টা করুন।"
            )
        else:
            await processing_msg.edit_text(
                f"❌ সমস্যা হয়েছে!\n\n"
                f"কারণ: {error_msg[:200]}\n\n"
                f"আবার চেষ্টা করুন বা @HSNK_TEAM এ যোগাযোগ করুন।"
            )

def main():
    """Bot চালু করো"""
    # Bot application তৈরি করো
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Message handler - যেকোনো টেক্সট মেসেজের জন্য
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    print("🤖 HSNK Downloader Bot চালু হয়েছে!")
    print("Bot বন্ধ করতে Ctrl+C চাপুন")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
