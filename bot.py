import telebot
import re
from flask import Flask, request
from os import getenv
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set API Key Telegram dan OpenAI
TOKEN = getenv("TELEGRAM_API_TOKEN")
TELEGRAM_API_TOKEN = getenv("TELEGRAM_API_TOKEN")
OPENAI_API_KEY = getenv("TOKEN_OPENAI_KEY")

# Inisialisasi OpenAI
openai.api_key = OPENAI_API_KEY

# Fungsi untuk menghubungkan OpenAI API
def get_ai_response(user_message: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",  # Atau model GPT lain yang Anda inginkan
        prompt=user_message,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Fungsi untuk menangani pesan masuk dari pengguna
def respond_to_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    ai_response = get_ai_response(user_message)
    update.message.reply_text(ai_response)

# Fungsi untuk start bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Halo! Saya adalah bot AI. Tanyakan apa saja!')

def main():
    # Inisialisasi Updater dan Dispatcher
    updater = Updater(TELEGRAM_API_TOKEN)
    dispatcher = updater.dispatcher

    # Menambahkan handler untuk command /start dan pesan masuk
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond_to_message))

    # Mulai bot
    updater.start_polling()
    updater.idle()
load_dotenv()


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
@bot.message_handler(content_types=["sticker"])
def auto_reply_sticker(message):
    bot.reply_to(message, "Stiker diterima! 🎉")


from telebot import types

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not message.from_user.id in ADMIN_IDS:
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

# Fungsi tambahan untuk membuat tombol
def kick_button(user_id):
    keyboard = types.InlineKeyboardMarkup()
    kick_button = types.InlineKeyboardButton("Kick", callback_data=f"kick_{user_id}")
    keyboard.add(kick_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith("kick_"))
def handle_kick(call):
    member_id = int(call.data.split("_")[1])
    chat_id = call.message.chat.id

    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "Hanya admin yang dapat menggunakan tombol ini!")
        return

    try:
        bot.kick_chat_member(chat_id, member_id)
        bot.answer_callback_query(call.id, "Anggota berhasil dikeluarkan!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Gagal mengeluarkan anggota: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "Kick User")
def prompt_kick(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Hanya admin yang dapat menggunakan fitur ini!")
        return

    member_id = ...  # Masukkan ID pengguna yang ingin dikeluarkan
    bot.send_message(
        message.chat.id,
        "Apakah Anda yakin ingin mengeluarkan anggota ini?",
        reply_markup=kick_button(member_id)
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
    bot.set_webhook(url=f"https://bottelegram-two.vercel.app/{TOKEN}")
    return "Bot is running!", 200


if __name__=="__main__":
    main()

if __name__ == "__main__":
    app.run(debug=True)
