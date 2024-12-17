import telebot
import re
from flask import Flask, request
from os import getenv
from dotenv import load_dotenv
import openai
from telebot import types

# Muat file .env jika Anda sedang mengembangkan secara lokal
load_dotenv()

# Ambil token dari environment variables
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
OPENAI_API_KEY = os.getenv("TOKEN_OPENAI_KEY")

# Sekarang Anda bisa menggunakan TELEGRAM_API_TOKEN dan OPENAI_API_KEY di kode Anda
openai.api_key = OPENAI_API_KEY

# Fungsi untuk menghubungkan OpenAI API
def get_ai_response(user_message: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",  # Atau model GPT lain yang Anda inginkan
        prompt=user_message,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Inisialisasi telebot untuk bot Telegram
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

# Auto-reply untuk stiker
@bot.message_handler(content_types=["sticker"])
def auto_reply_sticker(message):
    bot.reply_to(message, "Stiker diterima! 🎉")

# Fungsi untuk kick user
@bot.message_handler(commands=['kick'])
def kick_user(message):
    # Cek apakah pengirim adalah admin
    ADMIN_IDS = []  # Definisikan ID admin di sini
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Hanya admin yang dapat menggunakan perintah ini!")
        return

    chat_id = message.chat.id

    # Mendapatkan ID anggota yang ingin dikeluarkan
    try:
        member_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "Silakan gunakan format: /kick <user_id>")
        return

    try:
        bot.kick_chat_member(chat_id, member_id)
        bot.reply_to(message, f"Anggota dengan ID {member_id} telah dikeluarkan!")
    except Exception as e:
        bot.reply_to(message, f"Gagal mengeluarkan anggota: {str(e)}")

# Fungsi tambahan untuk membuat tombol Kick
def kick_button(user_id):
    keyboard = types.InlineKeyboardMarkup()
    kick_button = types.InlineKeyboardButton("Kick", callback_data=f"kick_{user_id}")
    keyboard.add(kick_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith("kick_"))
def handle_kick(call):
    member_id = int(call.data.split("_")[1])
    chat_id = call.message.chat.id

    # Cek apakah yang menekan tombol adalah admin
    ADMIN_IDS = []  # Definisikan ID admin di sini
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "Hanya admin yang dapat menggunakan tombol ini!")
        return

    try:
        bot.kick_chat_member(chat_id, member_id)
        bot.answer_callback_query(call.id, "Anggota berhasil dikeluarkan!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Gagal mengeluarkan anggota: {str(e)}")

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
    bot.set_webhook(url=f"https://{getenv('VERCEL_URL')}/{TOKEN}")
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=True)
