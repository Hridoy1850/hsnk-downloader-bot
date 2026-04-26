import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ============================================================
# সূরার তালিকা
# ============================================================

SURAHS = [
    (1,"আল-ফাতিহা","الفاتحة",7),(2,"আল-বাকারা","البقرة",286),(3,"আল-ইমরান","آل عمران",200),
    (4,"আন-নিসা","النساء",176),(5,"আল-মায়িদা","المائدة",120),(6,"আল-আনআম","الأنعام",165),
    (7,"আল-আরাফ","الأعراف",206),(8,"আল-আনফাল","الأنفال",75),(9,"আত-তাওবা","التوبة",129),
    (10,"ইউনুস","يونس",109),(11,"হুদ","هود",123),(12,"ইউসুফ","يوسف",111),
    (13,"আর-রাদ","الرعد",43),(14,"ইবরাহিম","إبراهيم",52),(15,"আল-হিজর","الحجر",99),
    (16,"আন-নাহল","النحل",128),(17,"আল-ইসরা","الإسراء",111),(18,"আল-কাহফ","الكهف",110),
    (19,"মারইয়াম","مريم",98),(20,"ত্বাহা","طه",135),(21,"আল-আম্বিয়া","الأنبياء",112),
    (22,"আল-হজ্জ","الحج",78),(23,"আল-মুমিনুন","المؤمنون",118),(24,"আন-নূর","النور",64),
    (25,"আল-ফুরকান","الفرقان",77),(26,"আশ-শুআরা","الشعراء",227),(27,"আন-নামল","النمل",93),
    (28,"আল-কাসাস","القصص",88),(29,"আল-আনকাবুত","العنكبوت",69),(30,"আর-রুম","الروم",60),
    (31,"লুকমান","لقمان",34),(32,"আস-সাজদা","السجدة",30),(33,"আল-আহযাব","الأحزاب",73),
    (34,"সাবা","سبأ",54),(35,"ফাতির","فاطر",45),(36,"ইয়া-সিন","يس",83),
    (37,"আস-সাফফাত","الصافات",182),(38,"সোয়াদ","ص",88),(39,"আয-যুমার","الزمر",75),
    (40,"গাফির","غافر",85),(41,"ফুসসিলাত","فصلت",54),(42,"আশ-শুরা","الشورى",53),
    (43,"আয-যুখরুফ","الزخرف",89),(44,"আদ-দুখান","الدخان",59),(45,"আল-জাসিয়া","الجاثية",37),
    (46,"আল-আহকাফ","الأحقاف",35),(47,"মুহাম্মদ","محمد",38),(48,"আল-ফাতহ","الفتح",29),
    (49,"আল-হুজুরাত","الحجرات",18),(50,"কাফ","ق",45),(51,"আয-যারিয়াত","الذاريات",60),
    (52,"আত-তুর","الطور",49),(53,"আন-নাজম","النجم",62),(54,"আল-কামার","القمر",55),
    (55,"আর-রাহমান","الرحمن",78),(56,"আল-ওয়াকিয়া","الواقعة",96),(57,"আল-হাদিদ","الحديد",29),
    (58,"আল-মুজাদালা","المجادلة",22),(59,"আল-হাশর","الحشر",24),(60,"আল-মুমতাহানা","الممتحنة",13),
    (61,"আস-সাফ","الصف",14),(62,"আল-জুমুআ","الجمعة",11),(63,"আল-মুনাফিকুন","المنافقون",11),
    (64,"আত-তাগাবুন","التغابن",18),(65,"আত-তালাক","الطلاق",12),(66,"আত-তাহরিম","التحريم",12),
    (67,"আল-মুলক","الملك",30),(68,"আল-কালাম","القلم",52),(69,"আল-হাককা","الحاقة",52),
    (70,"আল-মাআরিজ","المعارج",44),(71,"নূহ","نوح",28),(72,"আল-জিন","الجن",28),
    (73,"আল-মুযযাম্মিল","المزمل",20),(74,"আল-মুদ্দাস্সির","المدثر",56),(75,"আল-কিয়ামা","القيامة",40),
    (76,"আল-ইনসান","الإنسان",31),(77,"আল-মুরসালাত","المرسلات",50),(78,"আন-নাবা","النبأ",40),
    (79,"আন-নাযিআত","النازعات",46),(80,"আবাসা","عبس",42),(81,"আত-তাকভির","التكوير",29),
    (82,"আল-ইনফিতার","الانفطار",19),(83,"আল-মুতাফফিফিন","المطففين",36),(84,"আল-ইনশিকাক","الانشقاق",25),
    (85,"আল-বুরুজ","البروج",22),(86,"আত-তারিক","الطارق",17),(87,"আল-আলা","الأعلى",19),
    (88,"আল-গাশিয়া","الغاشية",26),(89,"আল-ফাজর","الفجر",30),(90,"আল-বালাদ","البلد",20),
    (91,"আশ-শামস","الشمس",15),(92,"আল-লাইল","الليل",21),(93,"আদ-দুহা","الضحى",11),
    (94,"আশ-শারহ","الشرح",8),(95,"আত-তিন","التين",8),(96,"আল-আলাক","العلق",19),
    (97,"আল-কাদর","القدر",5),(98,"আল-বাইয়িনা","البينة",8),(99,"আয-যালযালা","الزلزلة",8),
    (100,"আল-আদিয়াত","العاديات",11),(101,"আল-কারিআ","القارعة",11),(102,"আত-তাকাসুর","التكاثر",8),
    (103,"আল-আসর","العصر",3),(104,"আল-হুমাযা","الهمزة",9),(105,"আল-ফিল","الفيل",5),
    (106,"কুরাইশ","قريش",4),(107,"আল-মাউন","الماعون",7),(108,"আল-কাউসার","الكوثر",3),
    (109,"আল-কাফিরুন","الكافرون",6),(110,"আন-নাসর","النصر",3),(111,"আল-মাসাদ","المسد",5),
    (112,"আল-ইখলাস","الإخلاص",4),(113,"আল-ফালাক","الفلق",5),(114,"আন-নাস","الناس",6),
]

# ============================================================
# API ফাংশন
# ============================================================

def get_ayah(surah_num, ayah_num):
    """আরবি, বাংলা অর্থ ও উচ্চারণ আনো"""
    try:
        # আরবি
        arabic_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/ar.alafasy"
        arabic_resp = requests.get(arabic_url, timeout=10).json()
        arabic_text = arabic_resp["data"]["text"] if arabic_resp["status"] == "OK" else "❌"

        # বাংলা অর্থ
        bengali_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/bn.bengali"
        bengali_resp = requests.get(bengali_url, timeout=10).json()
        bengali_text = bengali_resp["data"]["text"] if bengali_resp["status"] == "OK" else "❌"

        # উচ্চারণ (transliteration)
        translit_url = f"https://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/en.transliteration"
        translit_resp = requests.get(translit_url, timeout=10).json()
        translit_text = translit_resp["data"]["text"] if translit_resp["status"] == "OK" else "❌"

        return arabic_text, translit_text, bengali_text
    except Exception as e:
        logging.error(f"API error: {e}")
        return None, None, None

def get_random_ayah():
    """Random আয়াত আনো"""
    import random
    surah = random.choice(SURAHS)
    ayah_num = random.randint(1, surah[3])
    return surah[0], surah[1], ayah_num

# ============================================================
# মেনু
# ============================================================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 সূরা নির্বাচন", callback_data="surah_list_1"),
         InlineKeyboardButton("🎲 Random আয়াত", callback_data="random_ayah")],
        [InlineKeyboardButton("🔢 আয়াত খোঁজো", callback_data="search_ayah"),
         InlineKeyboardButton("⭐ জনপ্রিয় আয়াত", callback_data="popular")],
        [InlineKeyboardButton("ℹ️ সাহায্য", callback_data="help")],
    ])

def surah_list_keyboard(page=1):
    """সূরার তালিকা — প্রতি পেজে ১০টি"""
    per_page = 10
    start = (page-1) * per_page
    end = start + per_page
    surahs_page = SURAHS[start:end]
    
    keyboard = []
    for surah in surahs_page:
        num, name_bn, name_ar, total = surah
        keyboard.append([InlineKeyboardButton(
            f"{num}. {name_bn} ({name_ar}) - {total} আয়াত",
            callback_data=f"surah_{num}_1"
        )])
    
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️ আগে", callback_data=f"surah_list_{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page}/{(len(SURAHS)+per_page-1)//per_page}", callback_data="noop"))
    if end < len(SURAHS):
        nav.append(InlineKeyboardButton("পরে ▶️", callback_data=f"surah_list_{page+1}"))
    keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

def ayah_keyboard(surah_num, ayah_num, total_ayahs):
    """আয়াত নেভিগেশন বাটন"""
    keyboard = []
    nav = []
    if ayah_num > 1:
        nav.append(InlineKeyboardButton("◀️ আগের আয়াত", callback_data=f"ayah_{surah_num}_{ayah_num-1}"))
    if ayah_num < total_ayahs:
        nav.append(InlineKeyboardButton("পরের আয়াত ▶️", callback_data=f"ayah_{surah_num}_{ayah_num+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([
        InlineKeyboardButton("📖 সূরায় ফিরো", callback_data=f"surah_{surah_num}_1"),
        InlineKeyboardButton("🏠 মেনু", callback_data="menu")
    ])
    return InlineKeyboardMarkup(keyboard)

# ============================================================
# জনপ্রিয় আয়াত
# ============================================================

POPULAR_AYAHS = [
    (2, 255, "আয়াতুল কুরসি"),
    (1, 1, "সূরা ফাতিহা - ১ম আয়াত"),
    (112, 1, "সূরা ইখলাস - ১ম আয়াত"),
    (36, 1, "সূরা ইয়াসিন - ১ম আয়াত"),
    (55, 1, "সূরা রাহমান - ১ম আয়াত"),
    (67, 1, "সূরা মুলক - ১ম আয়াত"),
    (18, 1, "সূরা কাহফ - ১ম আয়াত"),
    (2, 286, "সূরা বাকারা - শেষ আয়াত"),
]

def popular_keyboard():
    keyboard = []
    for surah_num, ayah_num, label in POPULAR_AYAHS:
        keyboard.append([InlineKeyboardButton(
            f"⭐ {label}", callback_data=f"ayah_{surah_num}_{ayah_num}"
        )])
    keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

# ============================================================
# COMMANDS
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ\n\n"
        f"আস্সালামু আলাইকুম *{name}* ভাই/আপু! 🌙\n\n"
        f"স্বাগতম *HSNK কোরআন Bot* এ!\n\n"
        f"এখানে পাবেন:\n"
        f"📖 পুরো কোরআনের ১১৪টি সূরা\n"
        f"🔤 আরবি মূল পাঠ\n"
        f"🗣️ বাংলা উচ্চারণ\n"
        f"📝 বাংলা অর্থ\n\n"
        f"আল্লাহ আমাদের সকলকে কোরআন বোঝার তৌফিক দান করুন। আমিন! 🤲",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ============================================================
# CALLBACK
# ============================================================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "noop":
        return

    # মেনু
    if data == "menu":
        await q.edit_message_text(
            "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ\n\n"
            "📖 *HSNK কোরআন Bot*\n\nকী করতে চান?",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    # সূরার তালিকা
    elif data.startswith("surah_list_"):
        page = int(data.split("_")[2])
        await q.edit_message_text(
            f"📖 *সূরার তালিকা* (পেজ {page})\n\nকোন সূরা পড়তে চান?",
            parse_mode="Markdown",
            reply_markup=surah_list_keyboard(page)
        )

    # সূরা সিলেক্ট
    elif data.startswith("surah_") and not data.startswith("surah_list"):
        parts = data.split("_")
        surah_num = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 1
        
        surah = next((s for s in SURAHS if s[0] == surah_num), None)
        if not surah:
            return
        
        _, name_bn, name_ar, total = surah
        per_page = 10
        start = (page-1) * per_page + 1
        end = min(start + per_page - 1, total)
        
        keyboard = []
        for ayah_num in range(start, end+1):
            keyboard.append([InlineKeyboardButton(
                f"আয়াত {ayah_num}", callback_data=f"ayah_{surah_num}_{ayah_num}"
            )])
        
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("◀️ আগে", callback_data=f"surah_{surah_num}_{page-1}"))
        if end < total:
            nav.append(InlineKeyboardButton("পরে ▶️", callback_data=f"surah_{surah_num}_{page+1}"))
        if nav:
            keyboard.append(nav)
        keyboard.append([InlineKeyboardButton("📋 সব সূরা", callback_data="surah_list_1"),
                         InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        
        await q.edit_message_text(
            f"📖 *{surah_num}. সূরা {name_bn}*\n"
            f"*{name_ar}*\n\n"
            f"মোট আয়াত: {total}\n\nকোন আয়াত পড়তে চান?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # আয়াত দেখাও
    elif data.startswith("ayah_"):
        parts = data.split("_")
        surah_num = int(parts[1])
        ayah_num = int(parts[2])
        
        surah = next((s for s in SURAHS if s[0] == surah_num), None)
        if not surah:
            return
        
        _, name_bn, name_ar, total = surah
        
        await q.edit_message_text(
            f"⏳ *{name_bn} - আয়াত {ayah_num}* লোড হচ্ছে...",
            parse_mode="Markdown"
        )
        
        arabic, translit, bengali = get_ayah(surah_num, ayah_num)
        
        if not arabic:
            await q.edit_message_text(
                "❌ ইন্টারনেট সমস্যা! আবার চেষ্টা করুন।",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data=data),
                                                    InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            return
        
        text = (
            f"📖 *সূরা {name_bn} ({name_ar})*\n"
            f"*আয়াত: {ayah_num}/{total}*\n\n"
            f"『 আরবি 』\n"
            f"{arabic}\n\n"
            f"『 বাংলা উচ্চারণ 』\n"
            f"_{translit}_\n\n"
            f"『 বাংলা অর্থ 』\n"
            f"{bengali}"
        )
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=ayah_keyboard(surah_num, ayah_num, total)
        )

    # Random আয়াত
    elif data == "random_ayah":
        await q.edit_message_text("⏳ Random আয়াত লোড হচ্ছে...")
        
        import random
        surah = random.choice(SURAHS)
        surah_num = surah[0]
        name_bn = surah[1]
        name_ar = surah[2]
        total = surah[3]
        ayah_num = random.randint(1, total)
        
        arabic, translit, bengali = get_ayah(surah_num, ayah_num)
        
        if not arabic:
            await q.edit_message_text(
                "❌ ইন্টারনেট সমস্যা! আবার চেষ্টা করুন।",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data="random_ayah"),
                                                    InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            return
        
        text = (
            f"🎲 *Random আয়াত*\n\n"
            f"📖 *সূরা {name_bn} ({name_ar})*\n"
            f"*আয়াত: {ayah_num}/{total}*\n\n"
            f"『 আরবি 』\n"
            f"{arabic}\n\n"
            f"『 বাংলা উচ্চারণ 』\n"
            f"_{translit}_\n\n"
            f"『 বাংলা অর্থ 』\n"
            f"{bengali}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 আরেকটি Random", callback_data="random_ayah")],
            [InlineKeyboardButton("📖 এই সূরা পড়ো", callback_data=f"surah_{surah_num}_1"),
             InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
        ])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # জনপ্রিয় আয়াত
    elif data == "popular":
        await q.edit_message_text(
            "⭐ *জনপ্রিয় আয়াতসমূহ*\n\nকোনটি পড়তে চান?",
            parse_mode="Markdown",
            reply_markup=popular_keyboard()
        )

    # সাহায্য
    elif data == "help":
        await q.edit_message_text(
            "ℹ️ *সাহায্য*\n\n"
            "📖 *সূরা নির্বাচন* — ১১৪টি সূরার তালিকা\n"
            "🎲 *Random আয়াত* — যেকোনো আয়াত\n"
            "⭐ *জনপ্রিয় আয়াত* — আয়াতুল কুরসি সহ বিখ্যাত আয়াত\n\n"
            "প্রতিটি আয়াতে থাকবে:\n"
            "🔤 আরবি মূল পাঠ\n"
            "🗣️ বাংলা উচ্চারণ\n"
            "📝 বাংলা অর্থ\n\n"
            "যেকোনো সমস্যায়: @HSNK_TEAM\n\n"
            "اللهم اجعل القرآن ربيع قلوبنا 🤲",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))

    # আয়াত খোঁজো
    elif data == "search_ayah":
        await q.edit_message_text(
            "🔢 *আয়াত খোঁজো*\n\n"
            "এভাবে লিখুন:\n"
            "`সূরা নম্বর:আয়াত নম্বর`\n\n"
            "উদাহরণ:\n"
            "`2:255` — আয়াতুল কুরসি\n"
            "`1:1` — সূরা ফাতিহার ১ম আয়াত\n"
            "`112:1` — সূরা ইখলাস",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # সূরা:আয়াত ফরম্যাট চেক
    if ":" in text:
        try:
            parts = text.split(":")
            surah_num = int(parts[0])
            ayah_num = int(parts[1])
            
            surah = next((s for s in SURAHS if s[0] == surah_num), None)
            if not surah or ayah_num < 1 or ayah_num > surah[3]:
                await update.message.reply_text(
                    "❌ সঠিক নম্বর দিন!\nযেমন: `2:255`",
                    parse_mode="Markdown"
                )
                return
            
            msg = await update.message.reply_text("⏳ লোড হচ্ছে...")
            arabic, translit, bengali = get_ayah(surah_num, ayah_num)
            
            if not arabic:
                await msg.edit_text("❌ ইন্টারনেট সমস্যা! আবার চেষ্টা করুন।")
                return
            
            name_bn = surah[1]
            name_ar = surah[2]
            total = surah[3]
            
            text_out = (
                f"📖 *সূরা {name_bn} ({name_ar})*\n"
                f"*আয়াত: {ayah_num}/{total}*\n\n"
                f"『 আরবি 』\n{arabic}\n\n"
                f"『 বাংলা উচ্চারণ 』\n_{translit}_\n\n"
                f"『 বাংলা অর্থ 』\n{bengali}"
            )
            await msg.edit_text(
                text_out, parse_mode="Markdown",
                reply_markup=ayah_keyboard(surah_num, ayah_num, total)
            )
            return
        except:
            pass
    
    await update.message.reply_text(
        "📖 *HSNK কোরআন Bot*\n\nমেনু থেকে বেছে নিন!",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("📖 HSNK কোরআন Bot চালু!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
