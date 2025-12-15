# ================= IMPORTS =================
import telebot
from telebot import types
import sqlite3
import datetime

# ================= CONFIG =================
BOT_TOKEN = "AAF5pm3Rq3-lyKSAbf64yOvlAv_igfg5qoI"  # Updated Token
ADMIN_IDS = [8253938305]
DB_FILE = "budhiraja_properties_bot.db"
BOT_NAME = "Budhiraja Properties"

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        name TEXT,
        phone TEXT,
        requirement TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_lead(uid, username, name, phone, requirement=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO leads VALUES (NULL,?,?,?,?,?,?)
    """, (
        uid,
        username,
        name,
        phone,
        requirement,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# ================= BOTTOM FIXED KEYBOARD =================
def bottom_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📞 Contact Us", "🌐 Visit Website")
    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"👋 Welcome to *{BOT_NAME}*\n\n"
        "👇 Please select an option below:",
        parse_mode="Markdown",
        reply_markup=bottom_menu()
    )

# ================= USER STATE =================
user_state = {}

# ================= LEAD FLOW =================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text

    if text == "📞 Contact Us":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            text="💬 WhatsApp",
            url="https://wa.me/917015409306?text=Hello%20Budhiraja%20Properties"
        ))
        bot.send_message(
            message.chat.id,
            "📞 Contact Us\n\nCall: 7015409306\nOr click below to WhatsApp us:",
            reply_markup=kb
        )
        return

    if text == "🌐 Visit Website":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            text="🌐 Visit Website",
            url="https://www.budhirajaservices.in"
        ))
        bot.send_message(
            message.chat.id,
            "Visit our website:",
            reply_markup=kb
        )
        return

    # Lead capture flow
    if message.chat.id not in user_state:
        user_state[message.chat.id] = {"step": "ask_name"}
        bot.send_message(
            message.chat.id,
            "📝 Please enter your full name:"
        )
        return

    step = user_state[message.chat.id]["step"]

    if step == "ask_name":
        user_state[message.chat.id]["name"] = text
        user_state[message.chat.id]["step"] = "ask_phone"
        bot.send_message(
            message.chat.id,
            "📱 Enter your mobile number:"
        )
        return

    if step == "ask_phone":
        user_state[message.chat.id]["phone"] = text
        user_state[message.chat.id]["step"] = "ask_requirement"
        bot.send_message(
            message.chat.id,
            "🖊 Please briefly describe your requirement:"
        )
        return

    if step == "ask_requirement":
        name = user_state[message.chat.id]["name"]
        phone = user_state[message.chat.id]["phone"]
        requirement = text
        user = message.from_user

        save_lead(user.id, user.username or "", name, phone, requirement)

        # Notify admin
        for admin in ADMIN_IDS:
            bot.send_message(
                admin,
                f"🔔 NEW LEAD\n\n"
                f"Name: {name}\n"
                f"Phone: {phone}\n"
                f"Requirement: {requirement}"
            )

        bot.send_message(
            message.chat.id,
            "✅ Thank you! We will contact you soon.",
            reply_markup=bottom_menu()
        )

        user_state.pop(message.chat.id, None)
        return

# ================= RUN =================
if __name__ == "__main__":
    init_db()
    print("🚀 Budhiraja Properties Bot Running...")
    bot.infinity_polling()
