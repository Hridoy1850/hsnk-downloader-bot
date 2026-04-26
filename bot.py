import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, 8716461364:AAFk92sxvI-L_3kqcOhd_UFmYRZcUXMJL-g
import json
import requests

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("8716461364:AAFk92sxvI-L_3kqcOhd_UFmYRZcUXMJL-g", "")

# ============================================================
# সূরা ও আয়াতের জন্য বাংলা নাম (সব সূরা)
# ============================================================

surah_bangla_names = {
    1: "আল-ফাতিহা", 2: "আল-বাকারাহ", 3: "আল-ইমরান", 4: "আন-নিসা", 5: "আল-মায়িদাহ",
    6: "আল-আনআম", 7: "আল-আরাফ", 8: "আল-আনফাল", 9: "আত-তাওবাহ", 10: "ইউনুস",
    11: "হুদ", 12: "ইউসুফ", 13: "আর-রাদ", 14: "ইব্রাহীম", 15: "আল-হিজর",
    16: "আন-নাহল", 17: "বনী ইসরাঈল", 18: "আল-কাহফ", 19: "মারইয়াম", 20: "ত্বোয়া-হা",
    21: "আল-আম্বিয়া", 22: "আল-হাজ্জ", 23: "আল-মুমিনুন", 24: "আন-নূর", 25: "আল-ফুরকান",
    26: "আশ-শুআরা", 27: "আন-নামল", 28: "আল-কাসাস", 29: "আল-আনকাবুত", 30: "আর-রুম",
    31: "লুকমান", 32: "আস-সাজদাহ", 33: "আল-আহযাব", 34: "সাবা", 35: "ফাতির",
    36: "ইয়াসীন", 37: "আস-সাফফাত", 38: "সোয়াদ", 39: "আজ-জুমার", 40: "গাফির",
    41: "হা-মীম", 42: "আশ-শূরা", 43: "আয-যুখরুফ", 44: "আদ-দোখান", 45: "আল-জাসিয়াহ",
    46: "আল-আহক্বাফ", 47: "মুহাম্মদ", 48: "আল-ফাতহ", 49: "আল-হুজুরাত", 50: "ক্বাফ",
    51: "আয-যারিয়াত", 52: "আত-তূর", 53: "আন-নাজম", 54: "আল-ক্বামার", 55: "আর-রাহমান",
    56: "আল-ওয়াকিয়াহ", 57: "আল-হাদিদ", 58: "আল-মুজাদালাহ", 59: "আল-হাশর", 60: "আল-মুমতাহিনাহ",
    61: "আস-সাফ", 62: "আল-জুমুআ", 63: "আল-মুনাফিকুন", 64: "আত-তাগাবুন", 65: "আত-তালাক",
    66: "আত-তাহরীম", 67: "আল-মুলক", 68: "আল-কালাম", 69: "আল-হাক্কাহ", 70: "আল-মাআরিজ",
    71: "নূহ", 72: "আল-জ্বিন", 73: "আল-মুযযাম্মিল", 74: "আল-মুদ্দাসসির", 75: "আল-ক্বিয়ামাহ",
    76: "আদ-দাহর", 77: "আল-মুরসালাত", 78: "আন-নাবা", 79: "আন-নাযিয়াত", 80: "আবাসা",
    81: "আত-তাকভীর", 82: "আল-ইনফিতার", 83: "আল-মুত্বাফফিফীন", 84: "আল-ইনশিকাক", 85: "আল-বুরুজ",
    86: "আত-তারিক্ব", 87: "আল-আ’লা", 88: "আল-গাশিয়াহ", 89: "আল-ফাজর", 90: "আল-বালাদ",
    91: "আশ-শামস", 92: "আল-লাইল", 93: "আদ-দুহা", 94: "আল-ইনশিরাহ", 95: "আত-তীন",
    96: "আল-আলাক", 97: "আল-ক্বদর", 98: "আল-বাইয়্যিনাহ", 99: "আজ-যিলযাল", 100: "আল-আদিয়াত",
    101: "আল-কারিয়াহ", 102: "আত-তাকাসুর", 103: "আল-আসর", 104: "আল-হুমাজাহ", 105: "আল-ফীল",
    106: "কুরাইশ", 107: "আল-মাউন", 108: "আল-কাওসার", 109: "আল-কাফিরুন", 110: "আন-নাসর",
    111: "আল-লাহাব", 112: "আল-ইখলাস", 113: "আল-ফালাক", 114: "আন-নাস"
}

# আয়াত সংখ্যা (প্রতি সূরার)
surah_ayah_count = {
    1:7, 2:286, 3:200, 4:176, 5:120, 6:165, 7:206, 8:75, 9:129, 10:109,
    11:123, 12:111, 13:43, 14:52, 15:99, 16:128, 17:111, 18:110, 19:98, 20:135,
    21:112, 22:78, 23:118, 24:64, 25:77, 26:227, 27:93, 28:88, 29:69, 30:60,
    31:34, 32:30, 33:73, 34:54, 35:45, 36:83, 37:182, 38:88, 39:75, 40:85,
    41:54, 42:53, 43:89, 44:59, 45:37, 46:35, 47:38, 48:29, 49:18, 50:45,
    51:60, 52:49, 53:62, 54:55, 55:78, 56:96, 57:29, 58:22, 59:24, 60:13,
    61:14, 62:11, 63:11, 64:18, 65:12, 66:12, 67:30, 68:52, 69:52, 70:44,
    71:28, 72:28, 73:20, 74:56, 75:40, 76:31, 77:50, 78:40, 79:46, 80:42,
    81:29, 82:19, 83:36, 84:25, 85:22, 86:17, 87:19, 88:26, 89:30, 90:20,
    91:15, 92:21, 93:11, 94:8, 95:8, 96:19, 97:5, 98:8, 99:8, 100:11,
    101:11, 102:8, 103:3, 104:9, 105:5, 106:4, 107:7, 108:3, 109:6, 110:3,
    111:5, 112:4, 113:5, 114:6
}

# ব্যবহারকারীর ডাটা
user_store = {}

def get_user(uid):
    if uid not in user_store:
        user_store[uid] = {"surah": 1, "ayah": 1}
    return user_store[uid]

def get_ayah_text(surah_num, ayah_num):
    """API থেকে আরবি ও বাংলা অর্থ আনে"""
    try:
        # আরবি
        ar_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/editions/quran-simple"
        ar_response = requests.get(ar_url, timeout=10).json()
        arabic = ar_response['data'][0]['text']
        
        # বাংলা অর্থ
        bn_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/bn.bengali"
        bn_response = requests.get(bn_url, timeout=10).json()
        bangla = bn_response['data']['text']
        
        return arabic, bangla
    except Exception as e:
        return "আয়াত পাওয়া যায়নি", "সংযোগ ত্রুটি, আবার চেষ্টা করুন"

def get_ayah_buttons(surah, ayah):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀ পিছন", callback_data=f"prev_{surah}_{ayah}"),
            InlineKeyboardButton("পরবর্তী ▶", callback_data=f"next_{surah}_{ayah}")
        ],
        [
            InlineKeyboardButton("🔄 সূরা পাল্টান", callback_data="change_surah"),
            InlineKeyboardButton("🔍 আয়াত সার্চ", callback_data="search_ayah")
        ],
        [InlineKeyboardButton("🏠 মেনুতে ফিরুন", callback_data="main_menu")]
    ])

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 কুরআন পড়ুন", callback_data="read_quran")],
        [InlineKeyboardButton("🔄 সূরা পরিবর্তন", callback_data="change_surah")],
        [InlineKeyboardButton("🔍 আয়াত খুঁজুন", callback_data="search_ayah")]
    ])

# ============================================================
# হ্যান্ডলার
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"📖 আসসালামু আলাইকুম, {name}!\n\n"
        f"পবিত্র কুরআন টেলিগ্রাম বোটে স্বাগতম।\n\n"
        f"নিচের মেনু থেকে কুরআন পড়া শুরু করুন।",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    data = query.data
    
    # মেনুতে ফেরা
    if data == "main_menu":
        await query.edit_message_text(
            "📖 *পবিত্র কুরআন বোট*\n\nনিচের অপশন বেছে নিন:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # কুরআন পড়া শুরু বা চালু রাখা
    if data == "read_quran":
        surah = user["surah"]
        ayah = user["ayah"]
        arabic, bangla = get_ayah_text(surah, ayah)
        
        msg = f"📌 *সূরা {surah_bangla_names.get(surah, surah)} : আয়াত {ayah}*\n\n"
        msg += f"🔹 *আরবি:*\n{arabic}\n\n"
        msg += f"🔸 *বাংলা অর্থ:*\n{bangla}"
        
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_ayah_buttons(surah, ayah)
        )
        return
    
    # পিছনের আয়াত
    if data.startswith("prev_"):
        parts = data.split("_")
        surah = int(parts[1])
        ayah = int(parts[2])
        
        if ayah > 1:
            ayah -= 1
        elif surah > 1:
            surah -= 1
            ayah = surah_ayah_count.get(surah, 7)
        
        user["surah"] = surah
        user["ayah"] = ayah
        
        arabic, bangla = get_ayah_text(surah, ayah)
        msg = f"📌 *সূরা {surah_bangla_names.get(surah, surah)} : আয়াত {ayah}*\n\n"
        msg += f"🔹 *আরবি:*\n{arabic}\n\n"
        msg += f"🔸 *বাংলা অর্থ:*\n{bangla}"
        
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_ayah_buttons(surah, ayah)
        )
        return
    
    # পরবর্তী আয়াত
    if data.startswith("next_"):
        parts = data.split("_")
        surah = int(parts[1])
        ayah = int(parts[2])
        max_ayah = surah_ayah_count.get(surah, 7)
        
        if ayah < max_ayah:
            ayah += 1
        elif surah < 114:
            surah += 1
            ayah = 1
        
        user["surah"] = surah
        user["ayah"] = ayah
        
        arabic, bangla = get_ayah_text(surah, ayah)
        msg = f"📌 *সূরা {surah_bangla_names.get(surah, surah)} : আয়াত {ayah}*\n\n"
        msg += f"🔹 *আরবি:*\n{arabic}\n\n"
        msg += f"🔸 *বাংলা অর্থ:*\n{bangla}"
        
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_ayah_buttons(surah, ayah)
        )
        return
    
    # সূরা পরিবর্তন
    if data == "change_surah":
        msg = "সূরা নম্বর লিখুন (1-114):\nউদাহরণ: 112 লিখলে সূরা ইখলাস দেখাবে"
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 বাতিল", callback_data="main_menu")]])
        )
        context.user_data['waiting_for_surah'] = True
        return
    
    # আয়াত সার্চ
    if data == "search_ayah":
        msg = "আয়াত নং লিখুন (সূরা:আয়াত ফরম্যাটে)\nউদাহরণ: 2:255 বা 112:2"
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 বাতিল", callback_data="main_menu")]])
        )
        context.user_data['waiting_for_ayah'] = True
        return

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user = get_user(user_id)
    
    # সূরা নম্বর ইনপুট
    if context.user_data.get('waiting_for_surah'):
        context.user_data['waiting_for_surah'] = False
        try:
            surah = int(text)
            if 1 <= surah <= 114:
                user["surah"] = surah
                user["ayah"] = 1
                
                arabic, bangla = get_ayah_text(surah, 1)
                msg = f"📌 *সূরা {surah_bangla_names.get(surah, surah)} : আয়াত 1*\n\n"
                msg += f"🔹 *আরবি:*\n{arabic}\n\n"
                msg += f"🔸 *বাংলা অর্থ:*\n{bangla}"
                
                await update.message.reply_text(
                    msg,
                    parse_mode="Markdown",
                    reply_markup=get_ayah_buttons(surah, 1)
                )
            else:
                await update.message.reply_text("❌ সূরা 1 থেকে 114 এর মধ্যে লিখুন।")
        except:
            await update.message.reply_text("❌ সঠিক সূরা নম্বর লিখুন (শুধু সংখ্যা)")
        return
    
    # আয়াত সার্চ ইনপুট
    if context.user_data.get('waiting_for_ayah'):
        context.user_data['waiting_for_ayah'] = False
        try:
            if ":" in text:
                surah, ayah = text.split(":")
                surah = int(surah)
                ayah = int(ayah)
                if 1 <= surah <= 114 and ayah >= 1:
                    max_ayah = surah_ayah_count.get(surah, 7)
                    if ayah <= max_ayah:
                        user["surah"] = surah
                        user["ayah"] = ayah
                        
                        arabic, bangla = get_ayah_text(surah, ayah)
                        msg = f"📌 *সূরা {surah_bangla_names.get(surah, surah)} : আয়াত {ayah}*\n\n"
                        msg += f"🔹 *আরবি:*\n{arabic}\n\n"
                        msg += f"🔸 *বাংলা অর্থ:*\n{bangla}"
                        
                        await update.message.reply_text(
                            msg,
                            parse_mode="Markdown",
                            reply_markup=get_ayah_buttons(surah, ayah)
                        )
                    else:
                        await update.message.reply_text(f"❌ সূরা {surah} -তে {max_ayah}টি আয়াত আছে।")
                else:
                    await update.message.reply_text("❌ সঠিক ফরম্যাট: সূরা:আয়াত (যেমন: 2:255)")
            else:
                await update.message.reply_text("❌ ফরম্যাট: সূরা:আয়াত (যেমন: 112:2)")
        except:
            await update.message.reply_text("❌ ত্রুটি! সঠিক ফরম্যাট: সূরা:আয়াত")
        return
    
    # অন্য যেকোনো টেক্সট
    await update.message.reply_text(
        "👇 মেনু থেকে অপশন বেছে নিন:",
        reply_markup=main_menu_keyboard()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 কুরআন বোট চালু হয়েছে!")
    print("টোকেন:", BOT_TOKEN[:20] + "...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
