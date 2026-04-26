import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ============================================================
# ডেটা
# ============================================================

FOOTBALL_QUIZ = [
    {"q": "⚽ বিশ্বকাপ ২০২২ কে জিতেছে?", "opts": ["ফ্রান্স", "আর্জেন্টিনা", "ব্রাজিল", "জার্মানি"], "ans": 1},
    {"q": "⚽ সবচেয়ে বেশি বিশ্বকাপ জেতা দেশ কোনটি?", "opts": ["জার্মানি", "আর্জেন্টিনা", "ব্রাজিল", "ইতালি"], "ans": 2},
    {"q": "⚽ মেসি কোন দেশের খেলোয়াড়?", "opts": ["ব্রাজিল", "উরুগুয়ে", "আর্জেন্টিনা", "স্পেন"], "ans": 2},
    {"q": "⚽ রোনালদো কোন দেশের খেলোয়াড়?", "opts": ["স্পেন", "পর্তুগাল", "ইতালি", "ফ্রান্স"], "ans": 1},
    {"q": "⚽ UCL সবচেয়ে বেশি জেতা ক্লাব কোনটি?", "opts": ["বার্সেলোনা", "ম্যান সিটি", "রিয়াল মাদ্রিদ", "বায়ার্ন"], "ans": 2},
    {"q": "⚽ FIFA র‍্যাংকিংয়ে শীর্ষে সবচেয়ে বেশিবার ছিল কে?", "opts": ["জার্মানি", "ব্রাজিল", "ফ্রান্স", "স্পেন"], "ans": 1},
    {"q": "⚽ প্রথম বিশ্বকাপ কোন সালে হয়েছিল?", "opts": ["১৯২৬", "১৯৩০", "১৯৩৪", "১৯৩৮"], "ans": 1},
    {"q": "⚽ নেইমার কোন দেশের খেলোয়াড়?", "opts": ["আর্জেন্টিনা", "কলম্বিয়া", "ব্রাজিল", "উরুগুয়ে"], "ans": 2},
    {"q": "⚽ বাংলাদেশের জাতীয় ফুটবল দলের ডাকনাম কী?", "opts": ["টাইগার্স", "বেঙ্গল", "লাল-সবুজ বাহিনী", "গ্যালাক্টিকোস"], "ans": 2},
    {"q": "⚽ এক ম্যাচে সর্বোচ্চ গোলের রেকর্ড কত?", "opts": ["১৪৯-০", "৩৬-০", "২০-০", "৫০-০"], "ans": 0},
    {"q": "⚽ মেসি কত বার ব্যালন ডি'অর জিতেছেন?", "opts": ["৬", "৭", "৮", "৯"], "ans": 2},
    {"q": "⚽ কোন ক্লাব 'গ্যালাক্টিকোস' নামে পরিচিত?", "opts": ["বার্সেলোনা", "রিয়াল মাদ্রিদ", "PSG", "ম্যান ইউ"], "ans": 1},
]

IQ_QUESTIONS = [
    {"q": "🧠 একটি মোরগ পূর্বদিকে তাকিয়ে ডিম পাড়লে ডিম কোথায় পড়বে?", "opts": ["পূর্বে", "পশ্চিমে", "নিচে", "মোরগ ডিম পাড়ে না"], "ans": 3, "exp": "মোরগ ডিম পাড়ে না — মুরগি পাড়ে! 🐓"},
    {"q": "🧠 ১+১+১+১+১×০+১ = কত?", "opts": ["০", "৬", "৫", "১"], "ans": 1, "exp": "BODMAS: ১×০=০, তাই ১+১+১+১+০+১=৫... আসলে ৬!"},
    {"q": "🧠 কোন জিনিস যত বেশি মোছে তত বেশি ভেজে?", "opts": ["কাপড়", "তোয়ালে", "স্পঞ্জ", "টিস্যু"], "ans": 1, "exp": "তোয়ালে যত মোছে তত ভেজে! 🛁"},
    {"q": "🧠 বেঁচে থাকা মানুষকে কোথায় সমাহিত করা হয়?", "opts": ["দেশে", "বিদেশে", "সমাহিত করা হয় না", "কবরে"], "ans": 2, "exp": "বেঁচে থাকলে সমাহিত করা হয় না! 😄"},
    {"q": "🧠 একটি ঘরে ৩টি বাতি আছে। ২টি জ্বললে কতটি নেভা?", "opts": ["১টি", "২টি", "৩টি", "০টি"], "ans": 0, "exp": "৩-২=১টি নেভা! 💡"},
    {"q": "🧠 কোন ট্রেন ইলেকট্রিক হলে ধোঁয়া কোনদিকে যাবে?", "opts": ["উত্তরে", "দক্ষিণে", "ধোঁয়া নেই", "বাতাসের দিকে"], "ans": 2, "exp": "ইলেকট্রিক ট্রেনে ধোঁয়া নেই! 🚆"},
    {"q": "🧠 Noah-র নৌকায় প্রতিটি প্রাণীর কয়টি করে ছিল?", "opts": ["১টি", "২টি", "৩টি", "৪টি"], "ans": 1, "exp": "জোড়ায় জোড়ায় — ২টি করে! 🐾"},
    {"q": "🧠 কোনটি ভারী — ১ কেজি তুলা নাকি ১ কেজি লোহা?", "opts": ["তুলা", "লোহা", "সমান", "নির্ভর করে"], "ans": 2, "exp": "দুটোই ১ কেজি — সমান ওজন! ⚖️"},
]

TRUTH_QUESTIONS = [
    "তোমার জীবনের সবচেয়ে বিব্রতকর মুহূর্ত কোনটি? 😳",
    "তুমি কি কখনো মিথ্যা বলে পার পেয়েছ? কীভাবে? 🤥",
    "তোমার সবচেয়ে গোপন স্বপ্ন কী? 🌙",
    "তুমি কার প্রেমে পড়েছিলে কিন্তু বলোনি? 💘",
    "তোমার সবচেয়ে বড় ভয় কী? 😱",
    "তুমি কি কখনো বন্ধুর পিছনে কথা বলেছ? 🗣️",
    "তোমার সবচেয়ে বড় রহস্য কী? 🤫",
    "তুমি কি কখনো পরীক্ষায় নকল করেছ? 📝",
    "তোমার জীবনের সবচেয়ে বড় ভুল কোনটি? 😅",
    "তুমি কোন জিনিসে সবচেয়ে বেশি টাকা নষ্ট করেছ? 💸",
]

DARE_CHALLENGES = [
    "এখনই ১০টি Push-up দাও! 💪",
    "নিজের সবচেয়ে মজার ছবি পাঠাও! 📸",
    "বাংলায় একটি Rap করো! 🎤",
    "তোমার পাশে যে আছে তাকে কমপ্লিমেন্ট দাও! 💝",
    "১ মিনিট চোখ বন্ধ রাখো! 👁️",
    "তোমার সেরা নাচের মুভ দেখাও! 💃",
    "উল্টো থেকে ১০ পর্যন্ত গণনা করো! 🔢",
    "তোমার প্রিয় গান গাও! 🎵",
    "৩০ সেকেন্ড এক পায়ে দাঁড়াও! 🦵",
    "তোমার সবচেয়ে মজার মুখভঙ্গি বানাও! 😜",
]

BLACKJACK_VALUES = {'A':11,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
SUITS = ['♠️','♥️','♦️','♣️']

# ============================================================
# হেল্পার ফাংশন
# ============================================================

user_store = {}

def get_user(uid):
    if uid not in user_store:
        user_store[uid] = {"coins": 500, "wins": 0, "losses": 0, "game_data": {}}
    return user_store[uid]

def hand_val(hand):
    total = sum(BLACKJACK_VALUES[r] for r,s in hand)
    aces = sum(1 for r,s in hand if r=='A')
    while total > 21 and aces:
        total -= 10; aces -= 1
    return total

def hand_str(hand):
    return ' '.join(f"{r}{s}" for r,s in hand)

def new_deck():
    d = [(r,s) for r in RANKS for s in SUITS]
    random.shuffle(d)
    return d

# ============================================================
# MINESWEEPER
# ============================================================

def make_board(size=5, mines=5):
    board = [[0]*size for _ in range(size)]
    mine_pos = set()
    while len(mine_pos) < mines:
        r,c = random.randint(0,size-1), random.randint(0,size-1)
        mine_pos.add((r,c))
    for r,c in mine_pos:
        board[r][c] = -1
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1: continue
            cnt = sum(1 for dr in [-1,0,1] for dc in [-1,0,1]
                      if 0<=r+dr<size and 0<=c+dc<size and board[r+dr][c+dc]==-1)
            board[r][c] = cnt
    return board, mine_pos

def board_keyboard(board, revealed, size=5, game_over=False):
    emojis = {-1:"💣", 0:"⬜", 1:"1️⃣", 2:"2️⃣", 3:"3️⃣", 4:"4️⃣", 5:"5️⃣"}
    keyboard = []
    for r in range(size):
        row = []
        for c in range(size):
            if (r,c) in revealed or game_over:
                val = board[r][c]
                cell = emojis.get(val, str(val))
            else:
                cell = "🟦"
            if not game_over and (r,c) not in revealed:
                row.append(InlineKeyboardButton(cell, callback_data=f"ms_{r}_{c}"))
            else:
                row.append(InlineKeyboardButton(cell, callback_data="noop"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

# ============================================================
# SNAKE GAME
# ============================================================

SNAKE_SIZE = 5

def make_snake_game():
    snake = [(2,2)]
    food = (random.randint(0,SNAKE_SIZE-1), random.randint(0,SNAKE_SIZE-1))
    while food in snake:
        food = (random.randint(0,SNAKE_SIZE-1), random.randint(0,SNAKE_SIZE-1))
    return {"snake": snake, "food": food, "direction": (0,1), "score": 0, "alive": True}

def render_snake(game):
    grid = [["⬛"]*SNAKE_SIZE for _ in range(SNAKE_SIZE)]
    r,c = game["food"]
    grid[r][c] = "🍎"
    for i,(sr,sc) in enumerate(game["snake"]):
        if 0<=sr<SNAKE_SIZE and 0<=sc<SNAKE_SIZE:
            grid[sr][sc] = "🟢" if i==0 else "🟩"
    return "\n".join("".join(row) for row in grid)

def move_snake(game, dr, dc):
    if not game["alive"]:
        return game
    head_r, head_c = game["snake"][0]
    new_head = (head_r+dr, head_c+dc)
    
    if not (0<=new_head[0]<SNAKE_SIZE and 0<=new_head[1]<SNAKE_SIZE):
        game["alive"] = False
        return game
    if new_head in game["snake"]:
        game["alive"] = False
        return game
    
    game["snake"].insert(0, new_head)
    if new_head == game["food"]:
        game["score"] += 10
        food = (random.randint(0,SNAKE_SIZE-1), random.randint(0,SNAKE_SIZE-1))
        while food in game["snake"]:
            food = (random.randint(0,SNAKE_SIZE-1), random.randint(0,SNAKE_SIZE-1))
        game["food"] = food
    else:
        game["snake"].pop()
    return game

def snake_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬆️", callback_data="snake_-1_0")],
        [InlineKeyboardButton("⬅️", callback_data="snake_0_-1"),
         InlineKeyboardButton("⬇️", callback_data="snake_1_0"),
         InlineKeyboardButton("➡️", callback_data="snake_0_1")],
        [InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
    ])

# ============================================================
# মেইন মেনু
# ============================================================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🃏 BlackJack", callback_data="bj_start"),
         InlineKeyboardButton("⚽ ফুটবল Quiz", callback_data="fq_start")],
        [InlineKeyboardButton("🧠 IQ Test", callback_data="iq_start"),
         InlineKeyboardButton("💣 Minesweeper", callback_data="ms_start")],
        [InlineKeyboardButton("🐍 Snake গেম", callback_data="snake_start"),
         InlineKeyboardButton("🎭 Truth or Dare", callback_data="tod_menu")],
        [InlineKeyboardButton("💰 আমার কয়েন", callback_data="mycoins")],
    ])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"🎉 স্বাগতম *{name}*!\n\n"
        f"🤖 *HSNK Mega Fun Bot*\n\n"
        f"💰 তোমার কয়েন: *{user['coins']}*\n\n"
        f"নিচ থেকে গেম বেছে নাও! 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ============================================================
# CALLBACK
# ============================================================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    user = get_user(uid)
    data = q.data

    if data == "noop":
        return

    # মেনু
    if data == "menu":
        await q.edit_message_text(
            f"🎮 *HSNK Mega Fun Bot*\n\n💰 কয়েন: *{user['coins']}*\n\nগেম বেছে নাও! 👇",
            parse_mode="Markdown", reply_markup=main_menu()
        )

    elif data == "mycoins":
        await q.edit_message_text(
            f"💰 *তোমার কয়েন: {user['coins']}*\n\n✅ জয়: {user['wins']}\n❌ হার: {user['losses']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))

    # ============================================================
    # BLACKJACK
    # ============================================================
    elif data == "bj_start":
        if user["coins"] < 100:
            await q.edit_message_text("❌ কয়েন কম! খেলতে ১০০ কয়েন লাগবে।", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            return
        deck = new_deck()
        ph = [deck.pop(), deck.pop()]
        dh = [deck.pop(), deck.pop()]
        user["game_data"]["bj"] = {"deck":deck, "player":ph, "dealer":dh}
        user["coins"] -= 100
        pv = hand_val(ph)
        await q.edit_message_text(
            f"🃏 *BlackJack!* (বাজি: 100 কয়েন)\n\n"
            f"👤 তোমার হাত: {hand_str(ph)} = *{pv}*\n"
            f"🤖 ডিলার: {ph[0][0]}{ph[0][1]} + ❓\n\nকী করবে?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👊 Hit", callback_data="bj_hit"),
                 InlineKeyboardButton("🛑 Stand", callback_data="bj_stand")],
                [InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

    elif data == "bj_hit":
        bj = user["game_data"].get("bj")
        if not bj:
            await q.edit_message_text("❌ নতুন গেম শুরু করো!", reply_markup=main_menu())
            return
        bj["player"].append(bj["deck"].pop())
        pv = hand_val(bj["player"])
        if pv > 21:
            user["losses"] += 1
            await q.edit_message_text(
                f"🃏 *BlackJack*\n\n👤 তোমার হাত: {hand_str(bj['player'])} = *{pv}*\n\n💥 Bust! হেরে গেছ! 😢\n💰 কয়েন: {user['coins']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data="bj_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            return
        await q.edit_message_text(
            f"🃏 *BlackJack*\n\n👤 তোমার হাত: {hand_str(bj['player'])} = *{pv}*\n🤖 ডিলার: {bj['dealer'][0][0]}{bj['dealer'][0][1]} + ❓\n\nকী করবে?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👊 Hit", callback_data="bj_hit"), InlineKeyboardButton("🛑 Stand", callback_data="bj_stand")],
                [InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

    elif data == "bj_stand":
        bj = user["game_data"].get("bj")
        if not bj:
            await q.edit_message_text("❌ নতুন গেম শুরু করো!", reply_markup=main_menu())
            return
        dv = hand_val(bj["dealer"])
        while dv < 17:
            bj["dealer"].append(bj["deck"].pop())
            dv = hand_val(bj["dealer"])
        pv = hand_val(bj["player"])
        if dv > 21 or pv > dv:
            user["coins"] += 220
            user["wins"] += 1
            result = "🎉 তুমি জিতেছ! +220 কয়েন!"
        elif pv == dv:
            user["coins"] += 100
            result = "🤝 ড্র! বাজি ফেরত!"
        else:
            user["losses"] += 1
            result = "😢 হেরেছ!"
        await q.edit_message_text(
            f"🃏 *BlackJack ফলাফল*\n\n👤 তুমি: {hand_str(bj['player'])} = *{pv}*\n🤖 ডিলার: {hand_str(bj['dealer'])} = *{dv}*\n\n{result}\n💰 কয়েন: {user['coins']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data="bj_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))

    # ============================================================
    # FOOTBALL QUIZ
    # ============================================================
    elif data == "fq_start":
        q_data = random.choice(FOOTBALL_QUIZ)
        user["game_data"]["fq"] = q_data
        keyboard = [[InlineKeyboardButton(f"{['A','B','C','D'][i]}) {opt}", callback_data=f"fq_{i}")] for i,opt in enumerate(q_data["opts"])]
        keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        await q.edit_message_text(
            f"⚽ *ফুটবল Quiz!*\n\n{q_data['q']}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("fq_"):
        ans = int(data[3:])
        q_data = user["game_data"].get("fq")
        if not q_data:
            await q.edit_message_text("❌ নতুন প্রশ্ন নাও!", reply_markup=main_menu())
            return
        if ans == q_data["ans"]:
            user["coins"] += 100
            user["wins"] += 1
            result = f"✅ *সঠিক! +100 কয়েন!* 🎉"
        else:
            user["losses"] += 1
            result = f"❌ *ভুল!*\nসঠিক: *{q_data['opts'][q_data['ans']]}*"
        await q.edit_message_text(
            f"{result}\n\n💰 কয়েন: {user['coins']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚽ আরেকটি", callback_data="fq_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))

    # ============================================================
    # IQ TEST
    # ============================================================
    elif data == "iq_start":
        q_data = random.choice(IQ_QUESTIONS)
        user["game_data"]["iq"] = q_data
        keyboard = [[InlineKeyboardButton(f"{['A','B','C','D'][i]}) {opt}", callback_data=f"iq_{i}")] for i,opt in enumerate(q_data["opts"])]
        keyboard.append([InlineKeyboardButton("🏠 মেনু", callback_data="menu")])
        await q.edit_message_text(
            f"🧠 *IQ Test!*\n\n{q_data['q']}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("iq_") and data[3:].isdigit():
        ans = int(data[3:])
        q_data = user["game_data"].get("iq")
        if not q_data:
            await q.edit_message_text("❌ নতুন প্রশ্ন নাও!", reply_markup=main_menu())
            return
        if ans == q_data["ans"]:
            user["coins"] += 150
            user["wins"] += 1
            result = f"✅ *সঠিক! +150 কয়েন!*\n\n💡 {q_data['exp']}"
        else:
            user["losses"] += 1
            result = f"❌ *ভুল!*\nসঠিক: *{q_data['opts'][q_data['ans']]}*\n💡 {q_data['exp']}"
        await q.edit_message_text(
            f"{result}\n\n💰 কয়েন: {user['coins']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧠 আরেকটি", callback_data="iq_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))

    # ============================================================
    # MINESWEEPER
    # ============================================================
    elif data == "ms_start":
        board, mines = make_board(5, 5)
        user["game_data"]["ms"] = {"board": board, "mines": mines, "revealed": set(), "size": 5, "safe": 25-5}
        await q.edit_message_text(
            "💣 *Minesweeper!*\n\n৫টি বোমা লুকিয়ে আছে!\nসব নিরাপদ ঘর খুললে জিতবে!\n\n🟦 = অজানা | ⬜ = নিরাপদ | 💣 = বোমা",
            parse_mode="Markdown",
            reply_markup=board_keyboard(board, set(), 5)
        )

    elif data.startswith("ms_") and data != "ms_start":
        parts = data.split("_")
        r, c = int(parts[1]), int(parts[2])
        ms = user["game_data"].get("ms")
        if not ms:
            await q.edit_message_text("❌ নতুন গেম শুরু করো!", reply_markup=main_menu())
            return
        board = ms["board"]
        revealed = ms["revealed"]
        
        if board[r][c] == -1:
            # বোমা!
            user["losses"] += 1
            await q.edit_message_text(
                f"💥 *BOOM! বোমা পেয়ে গেছ!*\n\nহেরে গেছ! 😢\n💰 কয়েন: {user['coins']}",
                parse_mode="Markdown",
                reply_markup=board_keyboard(board, revealed, 5, True)
            )
            user["game_data"].pop("ms", None)
            return
        
        revealed.add((r,c))
        ms["revealed"] = revealed
        remaining = ms["safe"] - len(revealed)
        
        if remaining <= 0:
            user["coins"] += 300
            user["wins"] += 1
            await q.edit_message_text(
                f"🎉 *জিতেছ! সব নিরাপদ ঘর খুলেছ!*\n+300 কয়েন! 💰\n\nমোট কয়েন: {user['coins']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data="ms_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            user["game_data"].pop("ms", None)
            return
        
        await q.edit_message_text(
            f"💣 *Minesweeper*\n\nবাকি নিরাপদ ঘর: *{remaining}*\nসাবধানে চালো!",
            parse_mode="Markdown",
            reply_markup=board_keyboard(board, revealed, 5)
        )

    # ============================================================
    # SNAKE
    # ============================================================
    elif data == "snake_start":
        game = make_snake_game()
        user["game_data"]["snake"] = game
        board = render_snake(game)
        await q.edit_message_text(
            f"🐍 *Snake গেম!*\n\nস্কোর: *{game['score']}*\n\n{board}\n\nতীর চাপো সাপ নাড়াতে!",
            parse_mode="Markdown", reply_markup=snake_keyboard()
        )

    elif data.startswith("snake_") and data != "snake_start":
        parts = data.split("_")
        dr, dc = int(parts[1]), int(parts[2])
        game = user["game_data"].get("snake")
        if not game:
            await q.edit_message_text("❌ নতুন গেম শুরু করো!", reply_markup=main_menu())
            return
        
        game = move_snake(game, dr, dc)
        
        if not game["alive"]:
            user["losses"] += 1
            user["coins"] += game["score"]
            await q.edit_message_text(
                f"💀 *Game Over!*\n\nস্কোর: *{game['score']}*\n+{game['score']} কয়েন পেয়েছ!\n💰 মোট: {user['coins']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 আবার", callback_data="snake_start"), InlineKeyboardButton("🏠 মেনু", callback_data="menu")]]))
            user["game_data"].pop("snake", None)
            return
        
        board = render_snake(game)
        await q.edit_message_text(
            f"🐍 *Snake গেম!*\n\nস্কোর: *{game['score']}*\n\n{board}\n\nতীর চাপো সাপ নাড়াতে!",
            parse_mode="Markdown", reply_markup=snake_keyboard()
        )

    # ============================================================
    # TRUTH OR DARE
    # ============================================================
    elif data == "tod_menu":
        await q.edit_message_text(
            "🎭 *Truth or Dare!*\n\nকী বেছে নেবে?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("😮 Truth", callback_data="tod_truth"),
                 InlineKeyboardButton("😈 Dare", callback_data="tod_dare")],
                [InlineKeyboardButton("🎲 Random", callback_data="tod_random"),
                 InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

    elif data == "tod_truth":
        question = random.choice(TRUTH_QUESTIONS)
        await q.edit_message_text(
            f"😮 *Truth প্রশ্ন:*\n\n{question}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 আরেকটি Truth", callback_data="tod_truth"),
                 InlineKeyboardButton("😈 Dare নাও", callback_data="tod_dare")],
                [InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

    elif data == "tod_dare":
        dare = random.choice(DARE_CHALLENGES)
        await q.edit_message_text(
            f"😈 *Dare চ্যালেঞ্জ:*\n\n{dare}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 আরেকটি Dare", callback_data="tod_dare"),
                 InlineKeyboardButton("😮 Truth নাও", callback_data="tod_truth")],
                [InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

    elif data == "tod_random":
        if random.choice([True, False]):
            question = random.choice(TRUTH_QUESTIONS)
            text = f"😮 *Truth প্রশ্ন:*\n\n{question}"
        else:
            dare = random.choice(DARE_CHALLENGES)
            text = f"😈 *Dare চ্যালেঞ্জ:*\n\n{dare}"
        await q.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 আবার Random", callback_data="tod_random"),
                 InlineKeyboardButton("🏠 মেনু", callback_data="menu")]
            ])
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👇 মেনু থেকে গেম বেছে নাও!", reply_markup=main_menu())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🎮 HSNK Mega Fun Bot চালু!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
