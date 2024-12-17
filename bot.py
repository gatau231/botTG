import telebot
import re
from flask import Flask, request
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("TELEGRAM_API_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Flask untuk Vercel
app = Flask(__name__)

# Daftar stiker terlarang (contoh: tambahkan ID stiker jorok di sini)
banned_stickers = ["CAACAgIAAxkBAAIBZGJor3QphRUC9ZoRZfbg8AABCrwAAeMZAAJWkEsKFnGgVJh44jYeBA"]

# Pesan selamat datang
@bot.message_handler(content_types=["new_chat_members"])
def greet_new_member(message):
    for new_member in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"👋 Selamat datang, {new_member.first_name}! Semoga betah di grup ini!"
        )

# Pesan perpisahan
@bot.message_handler(content_types=["left_chat_member"])
def farewell_member(message):
    bot.send_message(
        message.chat.id,
        f"👋 Selamat tinggal, {message.left_chat_member.first_name}. Semoga sukses ke depannya!"
    )

# Kick anggota yang mengirim stiker jorok
@bot.message_handler(content_types=["sticker"])
def handle_sticker(message):
    sticker_id = message.sticker.file_id
    if sticker_id in banned_stickers:
        bot.reply_to(message, "⚠️ Stiker ini tidak diperbolehkan!")
        bot.kick_chat_member(message.chat.id, message.from_user.id)

# Kick anggota yang berperilaku menipu
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Contoh pola untuk mendeteksi penipuan
    fraud_patterns = [
        r"(?i)jual akun",
        r"(?i)transfer uang",
        r"(?i)klik link ini",
        r"(?i)hadiah gratis"
    ]
    for pattern in fraud_patterns:
        if re.search(pattern, message.text):
            bot.reply_to(message, "⚠️ Pesan ini mencurigakan! Anda akan dikeluarkan.")
            bot.kick_chat_member(message.chat.id, message.from_user.id)
            return

# Webhook untuk Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# Homepage
@app.route("/")
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://bottelegram-five.vercel.app/{TOKEN}")
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=True)
