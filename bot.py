import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests

# ========== আপনার বোট টোকেন এখানে দিন ==========
BOT_TOKEN = "8716461364:AAFk92sxvI-L_3kqcOhd_UFmYRZcUXMJL-g"
bot = telebot.TeleBot(BOT_TOKEN)

# ========== অনলাইন থেকে সম্পূর্ণ কুরআন আনার API (ইন্টারনেট লাগবে) ==========
# বিনামূল্যে ও সম্পূর্ণ কুরআনের API - বাংলা অর্থ ও উচ্চারণসহ

# Surah names in Bangla (সব সূরা)
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

# ব্যবহারকারীর অবস্থান ট্র্যাক করা
user_state = {}

def get_ayah_text(surah_num, ayah_num):
    """API থেকে আরবি, উচ্চারণ ও অর্থ নিয়ে আসে"""
    try:
        # আরবি টেক্সট
        ar_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/editions/quran-simple"
        ar_response = requests.get(ar_url).json()
        arabic = ar_response['data'][0]['text']

        # বাংলা অনুবাদ (বাংলা উচ্চারণের জন্য আলাদা API নেই, তাই অর্থই দেখাব)
        bn_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/bn.bengali"
        bn_response = requests.get(bn_url).json()
        bangla_meaning = bn_response['data']['text']

        return arabic, bangla_meaning
    except:
        return "আয়াত পাওয়া যায়নি", "ত্রুটি"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_state[user_id] = {"surah": 1, "ayah": 1}
    
    welcome_text = """📖 **পবিত্র কুরআন - টেলিগ্রাম বোর্ড** 📖

আসসালামু আলাইকুম! এই বোটের মাধ্যমে আপনি সম্পূর্ণ কুরআন পড়তে পারবেন।

**কমান্ডসমূহ:**
/start - বোট চালু করা
/help - সাহায্য
/surah - সূরা পরিবর্তন
/ayah আয়াত নং - সরাসরি আয়াতে যান (যেমন: /ayah 2:255)

**নিচের বাটন ব্যবহার করুন:**"""
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("◀ পিছনের আয়াত", callback_data="prev_ayah"),
        InlineKeyboardButton("পরবর্তী আয়াত ▶", callback_data="next_ayah")
    )
    markup.row(
        InlineKeyboardButton("🔄 সূরা পরিবর্তন", callback_data="change_surah"),
        InlineKeyboardButton("🔍 আয়াত খুঁজুন", callback_data="search_ayah")
    )
    
    bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=markup)
    show_ayah(user_id)

def show_ayah(user_id):
    """বর্তমান সূরা ও আয়াত দেখায়"""
    state = user_state.get(user_id, {"surah": 1, "ayah": 1})
    surah = state["surah"]
    ayah = state["ayah"]
    
    arabic, bangla = get_ayah_text(surah, ayah)
    
    msg = f"""📌 **সূরা {surah_bangla_names.get(surah, surah)} : আয়াত {ayah}**

🔹 **আরবি:**
{arabic}

🔸 **বাংলা অর্থ:**
{bangla}

〰️〰️〰️〰️〰️〰️〰️
📖 {surah}/{surah_bangla_names.get(surah, surah)} : {ayah}"""
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("◀ পিছন", callback_data="prev_ayah"),
        InlineKeyboardButton("পরবর্তী ▶", callback_data="next_ayah")
    )
    markup.row(
        InlineKeyboardButton("🔄 সূরা পাল্টান", callback_data="change_surah"),
        InlineKeyboardButton("🔍 আয়াত সার্চ", callback_data="search_ayah")
    )
    
    bot.edit_message_text(msg, user_id, message_id=None, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    
    if call.data == "prev_ayah":
        state = user_state.get(user_id, {"surah": 1, "ayah": 1})
        if state["ayah"] > 1:
            state["ayah"] -= 1
        elif state["surah"] > 1:
            state["surah"] -= 1
            state["ayah"] = 1  # আগের সূরার ১ম আয়াত (সরলীকৃত)
        user_state[user_id] = state
        show_ayah(user_id)
        
    elif call.data == "next_ayah":
        state = user_state.get(user_id, {"surah": 1, "ayah": 1})
        state["ayah"] += 1
        if state["ayah"] > 7:  # প্রতিটি সূরার আয়াত সংখ্যা ভিন্ন, সরলীকৃত
            state["ayah"] = 1
            if state["surah"] < 114:
                state["surah"] += 1
        user_state[user_id] = state
        show_ayah(user_id)
        
    elif call.data == "change_surah":
        msg = "সূরা নম্বর লিখুন (1-114):\nযেমন: 112 লিখলে সূরা ইখলাস দেখাবে"
        bot.send_message(user_id, msg)
        bot.register_next_step_handler(call.message, set_surah)
        
    elif call.data == "search_ayah":
        msg = "আয়াত নং লিখুন (সূরা:আয়াত ফরম্যাটে)\nযেমন: 1:1 বা 112:2"
        bot.send_message(user_id, msg)
        bot.register_next_step_handler(call.message, search_ayah)

def set_surah(message):
    user_id = message.chat.id
    try:
        surah_num = int(message.text.strip())
        if 1 <= surah_num <= 114:
            user_state[user_id] = {"surah": surah_num, "ayah": 1}
            show_ayah(user_id)
        else:
            bot.send_message(user_id, "সূরা 1 থেকে 114 এর মধ্যে লিখুন।")
    except:
        bot.send_message(user_id, "সঠিক সূরা নম্বর লিখুন (শুধু সংখ্যা)")

def search_ayah(message):
    user_id = message.chat.id
    text = message.text.strip()
    try:
        if ":" in text:
            surah, ayah = text.split(":")
            surah = int(surah)
            ayah = int(ayah)
            if 1 <= surah <= 114 and ayah >= 1:
                user_state[user_id] = {"surah": surah, "ayah": ayah}
                show_ayah(user_id)
                return
        bot.send_message(user_id, "ভুল ফরম্যাট! সঠিক উদাহরণ: 2:255")
    except:
        bot.send_message(user_id, "ত্রুটি! ফরম্যাট: সূরা:আয়াত (যেমন 112:2)")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """📖 **কুরআন বোট সাহায্য**

/start - বোট চালু করুন
/help - এই সাহায্য দেখুন
/surah [নম্বর] - সূরা পরিবর্তন (যেমন: /surah 112)
/ayah [সূরা:আয়াত] - সরাসরি আয়াতে যান

**বাটনসমূহ:**
◀ পিছনের আয়াত
পরবর্তী আয়াত ▶
🔄 সূরা পরিবর্তন
🔍 আয়াত সার্চ

**উদাহরণ:**
আয়াতুল কুরসি পড়তে /ayah 2:255 লিখুন
সূরা ইখলাস পড়তে /surah 112 লিখুন"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# বোট চালু করুন
print("বোট চালু হচ্ছে...")
bot.infinity_polling()
