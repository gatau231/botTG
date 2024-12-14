import telebot
import uuid
from flask import Flask, request
from os import getenv
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("TELEGRAM_API_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Flask untuk Vercel
app = Flask(__name__)

# Dictionary untuk menyimpan lisensi
licenses = {}

# Command /start
@bot.message_handler(commands=['start'])
def start(message):
    welcome_message = f"""
Selamat datang, {message.from_user.first_name}!

📌 *Tentang Bot Ini:*
Bot ini digunakan untuk memverifikasi lisensi script Python Anda dan memberikan informasi perangkat.

🛠️ *Cara Menggunakan:*
1. Gunakan perintah `/generate_license` untuk membuat lisensi.
2. Gunakan perintah `/verify_license <license_key>` untuk memverifikasi lisensi Anda.
3. Gunakan perintah `/device_info` untuk melihat informasi perangkat Anda.
4. Gunakan perintah `/set_expiry <license_key> <hari>` untuk mengubah tanggal kedaluwarsa lisensi (Admin saja).
    """
    bot.reply_to(message, welcome_message, parse_mode="Markdown")

# Command /generate_license
@bot.message_handler(commands=['generate_license'])
def generate_license(message):
    user_id = message.chat.id

    # Cek apakah lisensi sudah pernah dibuat
    if user_id in licenses:
        bot.reply_to(
            message,
            f"Anda sudah memiliki lisensi: `{licenses[user_id]['key']}`\n"
            f"📅 Dibuat pada: `{licenses[user_id]['created_at']}`\n"
            f"⏳ Kedaluwarsa: `{licenses[user_id]['expires_at']}`",
            parse_mode="Markdown"
        )
        return

    # Buat lisensi baru
    license_key = str(uuid.uuid4())
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=30)  # Default 30 hari

    licenses[user_id] = {
        "key": license_key,
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Mengirimkan pesan lisensi yang dihasilkan
    message_text = f"🔑 Lisensi berhasil dibuat:\nLisensi: `{license_key}`\nDibuat: `{licenses[user_id]['created_at']}`\nKedaluwarsa: `{licenses[user_id]['expires_at']}`"
    bot.reply_to(message, message_text, parse_mode="Markdown")

    # Setelah mengirimkan pesan, bot akan memproses pesan yang dikirim (membaca dan mengaksesnya)
    read_message_from_bot(message)

# Fungsi untuk membaca pesan yang dikirim oleh bot
def read_message_from_bot(message):
    # Mendapatkan ID pesan yang dikirim oleh bot
    message_id = message.message_id
    chat_id = message.chat.id

    # Akses pesan yang baru dikirim oleh bot menggunakan message_id
    print(f"Bot mengirimkan pesan dengan ID: {message_id} ke chat ID: {chat_id}")
    print(f"Pesan yang dikirim oleh bot: {message.text}")

    # Simulasi mengakses pesan yang dikirim
    # Jika perlu, simpan informasi ini atau lakukan aksi lainnya
    if 'Lisensi berhasil dibuat' in message.text:
        print(f"Lisensi yang dibuat: {message.text}")
    else:
        print("Pesan tidak mengandung informasi lisensi.")

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
