import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ============================================================
# ডেটা
# ============================================================

JOKES = [
    "একজন মানুষ ডাক্তারের কাছে গেল।\nডাক্তার: কী সমস্যা?\nলোক: আমি যা খাই তাই হজম হয় না!\nডাক্তার: কী খেয়েছেন?\nলোক: গতকাল ১০০ টাকার নোট খেয়েছি! 😂",
    "শিক্ষক: তোমার বাবা কী করেন?\nছাত্র: ঘুমান স্যার!\nশিক্ষক: মানে?\nছাত্র: রাতে জেগে থাকেন, দিনে ঘুমান — নাইট গার্ড! 😄",
    "বউ: তুমি কি আমাকে ভালোবাসো?\nস্বামী: হ্যাঁ!\nবউ: কতটুকু?\nস্বামী: WiFi পাসওয়ার্ড দিয়ে দিলাম — এর চেয়ে বেশি ভালোবাসা কি হয়? 😁",
    "ছেলে: বাবা, আমি ফেল করেছি!\nবাবা: কতটুকু?\nছেলে: সব বিষয়ে!\nবাবা: চল তোকে স্কুলে ভর্তি করে দিই... নাকি সরাসরি চাকরিতে? 😅",
    "এক ব্যক্তি ব্যাংকে গেল।\nম্যানেজার: কত টাকা রাখবেন?\nলোক: ১০ টাকা!\nম্যানেজার: এত কম কেন?\nলোক: ATM Card দরকার ছিল! 🤣",
    "রিকশাওয়ালা: ভাই, ভাড়া ২০ টাকা!\nযাত্রী: ১০ টাকা দেবো!\nরিকশাওয়ালা: ঠিক আছে, তাহলে আমি ১০ টাকার পথ যাবো! 😂",
    "মা: পড়তে বসো!\nছেলে: এখন রাত ১২টা!\nমা: তাহলে এত রাতে মোবাইল চালাচ্ছ কেন?\nছেলে: ... 😶",
    "বন্ধু: তুই কি প্রেমে পড়েছিস?\nবন্ধু ২: না, আমি সিঁড়িতে পড়েছিলাম!\nবন্ধু: সেটাও তো প্রেম!\nবন্ধু ২: হ্যাঁ, সিঁড়ির সাথে! 😄",
]

ROASTS = [
    "তোমার চেহারা দেখে আয়নাও লজ্জা পায়! 😂",
    "তুমি এতটাই অলস যে, শ্বাস নিতেও ভুলে যাও মাঝে মাঝে! 😅",
    "তোমার IQ এবং তোমার বয়স — দুটোই এক সংখ্যার! 🤣",
    "তুমি এত বোকা যে, Google Maps ও তোমাকে হারিয়ে ফেলে! 😆",
    "তোমার মাথায় কি মগজ আছে, নাকি WiFi Router? কারণ কিছুই কাজ করে না! 😂",
    "তুমি এতটাই ধীর যে, Slow Motion ভিডিওতেও তোমাকে ধরা যায় না! 😄",
    "তোমার কথা শুনে ঘুম আসে — তুমি কি ঘুমের ওষুধ কোম্পানিতে কাজ করো? 😴",
    "তোমার সাথে কথা বলা মানে সময় নষ্ট — কিন্তু তুমি তো এমনিতেও সময় নষ্ট করো! 🤭",
]

FORTUNES = [
    "⭐ আজ তোমার দিন অসাধারণ হবে! নতুন কিছু পাবে!",
    "💰 শীঘ্রই টাকা আসবে — কিন্তু খরচও হবে! সাবধান!",
    "❤️ প্রেমের ক্ষেত্রে আজ ভালো খবর আসতে পারে!",
    "😴 আজ বিশ্রাম নাও — শরীর ক্লান্ত আছে!",
    "🌟 তোমার ভাগ্য আজ তোমার পক্ষে — সাহস করো!",
    "⚠️ আজ সতর্ক থাকো — কোনো বড় সিদ্ধান্ত নেওয়া ঠিক হবে না!",
    "🎯 তোমার লক্ষ্যে অটল থাকো — সফলতা আসছে!",
    "👫 বন্ধুদের সাথে সময় কাটাও — আজ মজা হবে!",
    "📚 পড়াশোনায় মনোযোগ দাও — পরীক্ষায় ভালো করবে!",
    "🚗 আজ ভ্রমণে ভালো কিছু হবে!",
]

RASHIFOL = {
    "মেষ": "🐏 আজ তোমার শক্তি অনেক বেশি। নতুন কাজ শুরু করো!",
    "বৃষ": "🐂 অর্থনৈতিক দিক থেকে আজ ভালো দিন।",
    "মিথুন": "👫 বন্ধুত্বে নতুন মাত্রা আসবে আজ।",
    "কর্কট": "🦀 পরিবারের সাথে সময় কাটাও — ভালো লাগবে।",
    "সিংহ": "🦁 আজ তুমি সবার মনোযোগ পাবে!",
    "কন্যা": "👩 কাজে সতর্ক থাকো — ভুল হতে পারে।",
    "তুলা": "⚖️ সম্পর্কে ভারসাম্য রাখো আজ।",
    "বৃশ্চিক": "🦂 রহস্যময় কিছু ঘটতে পারে আজ!",
    "ধনু": "🏹 দূরে যাওয়ার পরিকল্পনা করো — ভালো হবে।",
    "মকর": "🐐 ধৈর্য রাখো — সাফল্য আসছে।",
    "কুম্ভ": "🏺 নতুন আইডিয়া মাথায় আসবে আজ।",
    "মীন": "🐟 স্বপ্ন দেখো — কিছু একটা পাবে!",
}

QUIZ_QUESTIONS = [
    {
        "q": "বাংলাদেশের জাতীয় ফুল কী?",
        "options": ["গোলাপ", "শাপলা", "জুঁই", "পদ্ম"],
        "answer": 1
    },
    {
        "q": "বাংলাদেশ স্বাধীন হয় কত সালে?",
        "options": ["১৯৪৭", "১৯৬৯", "১৯৭১", "১৯৭৫"],
        "answer": 2
    },
    {
        "q": "পৃথিবীর সবচেয়ে বড় দেশ কোনটি?",
        "options": ["চীন", "আমেরিকা", "রাশিয়া", "কানাডা"],
        "answer": 2
    },
    {
        "q": "সূর্য থেকে পৃথিবীর দূরত্ব কত?",
        "options": ["১৫ কোটি কিমি", "২০ কোটি কিমি", "১০ কোটি কিমি", "৫ কোটি কিমি"],
        "answer": 0
    },
    {
        "q": "বাংলাদেশের জাতীয় পাখি কী?",
        "options": ["ময়না", "দোয়েল", "কোকিল", "শালিক"],
        "answer": 1
    },
    {
        "q": "১ কিলোবাইট = কত বাইট?",
        "options": ["৫১২", "১০০০", "১০২৪", "২০৪৮"],
        "answer": 2
    },
    {
        "q": "মানুষের শরীরে কতটি হাড় আছে?",
        "options": ["২০৬", "১৯৮", "২১২", "২২০"],
        "answer": 0
    },
    {
        "q": "বিশ্বের সবচেয়ে জনবহুল দেশ কোনটি (২০২৪)?",
        "options": ["চীন", "ভারত", "আমেরিকা", "ইন্দোনেশিয়া"],
        "answer": 1
    },
]

# User quiz state
user_quiz = {}
user_scores = {}

# ============================================================
# MAIN MENU
# ============================================================

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("😂 জোকস", callback_data="jokes"),
         InlineKeyboardButton("🔥 রোস্ট করো", callback_data="roast")],
        [InlineKeyboardButton("🔮 ভাগ্য দেখো", callback_data="fortune"),
         InlineKeyboardButton("🌟 রাশিফল", callback_data="rashifol")],
        [InlineKeyboardButton("🎮 Quiz খেলো", callback_data="quiz"),
         InlineKeyboardButton("🎲 লটারি", callback_data="lottery")],
        [InlineKeyboardButton("🎯 সংখ্যা অনুমান", callback_data="guess")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"🎉 আস্সালামু আলাইকুম *{name}*!\n\n"
        f"আমি *HSNK Fun Bot* 🤖\n\n"
        f"আমার সাথে মজা করুন!\n"
        f"নিচ থেকে যেকোনো অপশন বেছে নিন 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 *HSNK Fun Bot - সব কমান্ড:*\n\n"
        "/start - মেইন মেনু\n"
        "/joke - একটি জোকস\n"
        "/roast - রোস্ট করো\n"
        "/fortune - ভাগ্য দেখো\n"
        "/quiz - Quiz শুরু করো\n"
        "/lottery - লটারি খেলো\n"
        "/score - তোমার স্কোর\n\n"
        "অথবা নিচের বাটন চাপুন! 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# ============================================================
# JOKES
# ============================================================

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = random.choice(JOKES)
    keyboard = [[InlineKeyboardButton("😂 আরেকটি জোকস", callback_data="jokes"),
                 InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
    
    if update.message:
        await update.message.reply_text(
            f"😂 *মজার জোকস:*\n\n{joke}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ============================================================
# LOTTERY
# ============================================================

async def lottery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    numbers = sorted(random.sample(range(1, 50), 6))
    lucky = random.choice(["🍀 অনেক ভাগ্যবান!", "⭐ আজ তোমার দিন!", "💰 টাকা আসছে!", "😅 আবার চেষ্টা করো!"])
    
    keyboard = [[InlineKeyboardButton("🎲 আবার খেলো", callback_data="lottery"),
                 InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
    
    text = (f"🎰 *লটারি নম্বর:*\n\n"
            f"{'  '.join([f'`{n}`' for n in numbers])}\n\n"
            f"{lucky}")
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# QUIZ
# ============================================================

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = 0
    
    q_index = random.randint(0, len(QUIZ_QUESTIONS) - 1)
    user_quiz[user_id] = q_index
    
    q = QUIZ_QUESTIONS[q_index]
    keyboard = []
    for i, opt in enumerate(q["options"]):
        keyboard.append([InlineKeyboardButton(f"{['A','B','C','D'][i]}) {opt}", callback_data=f"quiz_ans_{i}")])
    keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
    
    text = f"🎮 *Quiz প্রশ্ন:*\n\n{q['q']}"
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score = user_scores.get(user_id, 0)
    await update.message.reply_text(
        f"🏆 *তোমার Quiz স্কোর:* {score} পয়েন্ট\n\n"
        f"আরো খেলো এবং স্কোর বাড়াও! 🎮",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# ============================================================
# CALLBACK HANDLER
# ============================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    # মেনু
    if data == "menu":
        await query.edit_message_text(
            "🎉 *HSNK Fun Bot মেনু*\n\nনিচ থেকে বেছে নিন 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # জোকস
    elif data == "jokes":
        joke = random.choice(JOKES)
        keyboard = [[InlineKeyboardButton("😂 আরেকটি", callback_data="jokes"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(
            f"😂 *মজার জোকস:*\n\n{joke}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # রোস্ট
    elif data == "roast":
        roast = random.choice(ROASTS)
        keyboard = [[InlineKeyboardButton("🔥 আরেকটি রোস্ট", callback_data="roast"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(
            f"🔥 *রোস্ট:*\n\n{roast}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ভাগ্য
    elif data == "fortune":
        fortune = random.choice(FORTUNES)
        keyboard = [[InlineKeyboardButton("🔮 আবার দেখো", callback_data="fortune"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(
            f"🔮 *তোমার ভাগ্য:*\n\n{fortune}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # রাশিফল
    elif data == "rashifol":
        keyboard = []
        row = []
        for i, rashi in enumerate(RASHIFOL.keys()):
            row.append(InlineKeyboardButton(rashi, callback_data=f"rashi_{rashi}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        await query.edit_message_text(
            "🌟 *রাশিফল দেখো!*\n\nতোমার রাশি বেছে নাও:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # রাশি সিলেক্ট
    elif data.startswith("rashi_"):
        rashi = data.replace("rashi_", "")
        result = RASHIFOL.get(rashi, "রাশি পাওয়া যায়নি!")
        keyboard = [[InlineKeyboardButton("🌟 অন্য রাশি", callback_data="rashifol"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(
            f"🌟 *{rashi} রাশি:*\n\n{result}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Quiz
    elif data == "quiz":
        q_index = random.randint(0, len(QUIZ_QUESTIONS) - 1)
        user_quiz[user_id] = q_index
        q = QUIZ_QUESTIONS[q_index]
        keyboard = []
        for i, opt in enumerate(q["options"]):
            keyboard.append([InlineKeyboardButton(f"{['A','B','C','D'][i]}) {opt}", callback_data=f"quiz_ans_{i}")])
        keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        await query.edit_message_text(
            f"🎮 *Quiz প্রশ্ন:*\n\n{q['q']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Quiz উত্তর
    elif data.startswith("quiz_ans_"):
        ans = int(data.replace("quiz_ans_", ""))
        q_index = user_quiz.get(user_id)
        
        if q_index is None:
            await query.edit_message_text("❌ নতুন প্রশ্ন নাও!", reply_markup=main_menu_keyboard())
            return
        
        q = QUIZ_QUESTIONS[q_index]
        if user_id not in user_scores:
            user_scores[user_id] = 0
        
        if ans == q["answer"]:
            user_scores[user_id] += 10
            result = f"✅ *সঠিক উত্তর!* +10 পয়েন্ট\n\n🏆 মোট স্কোর: {user_scores[user_id]}"
        else:
            correct = q["options"][q["answer"]]
            result = f"❌ *ভুল উত্তর!*\n\nসঠিক উত্তর: *{correct}*\n\n🏆 মোট স্কোর: {user_scores[user_id]}"
        
        keyboard = [[InlineKeyboardButton("🎮 আরেকটি প্রশ্ন", callback_data="quiz"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(result, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # লটারি
    elif data == "lottery":
        numbers = sorted(random.sample(range(1, 50), 6))
        lucky = random.choice(["🍀 অনেক ভাগ্যবান!", "⭐ আজ তোমার দিন!", "💰 টাকা আসছে!", "😅 আবার চেষ্টা করো!"])
        keyboard = [[InlineKeyboardButton("🎲 আবার খেলো", callback_data="lottery"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(
            f"🎰 *লটারি নম্বর:*\n\n{'  '.join([f'`{n}`' for n in numbers])}\n\n{lucky}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # সংখ্যা অনুমান
    elif data == "guess":
        number = random.randint(1, 10)
        context.user_data["guess_number"] = number
        keyboard = []
        row = []
        for i in range(1, 11):
            row.append(InlineKeyboardButton(str(i), callback_data=f"guess_{i}"))
            if len(row) == 5:
                keyboard.append(row)
                row = []
        keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        await query.edit_message_text(
            "🎯 *সংখ্যা অনুমান!*\n\n১ থেকে ১০ এর মধ্যে একটি সংখ্যা বেছে নিয়েছি!\nতুমি কি বলতে পারবে?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("guess_"):
        guessed = int(data.replace("guess_", ""))
        correct = context.user_data.get("guess_number", 0)
        
        if guessed == correct:
            result = f"🎉 *অসাধারণ! সঠিক!*\n\nসংখ্যাটি ছিল {correct}!\nতুমি জিতেছো! 🏆"
            if user_id not in user_scores:
                user_scores[user_id] = 0
            user_scores[user_id] += 20
        else:
            result = f"😅 *ভুল!*\n\nসংখ্যাটি ছিল *{correct}*!\nআবার চেষ্টা করো!"
        
        keyboard = [[InlineKeyboardButton("🎯 আবার খেলো", callback_data="guess"),
                     InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]
        await query.edit_message_text(result, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# TEXT HANDLER
# ============================================================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😊 মেনু থেকে বেছে নিন!",
        reply_markup=main_menu_keyboard()
    )

# ============================================================
# MAIN
# ============================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("lottery", lottery_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🎉 HSNK Fun Bot চালু হয়েছে!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
