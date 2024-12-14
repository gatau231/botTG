import telebot
import platform
import uuid
from flask import Flask, request
from os import getenv
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
    welcome_message = (
        f"Selamat datang, {message.from_user.first_name}!\n\n"
        "📌 *Tentang Bot Ini:*\n"
        "Bot ini digunakan untuk memverifikasi lisensi script Python Anda dan memberikan informasi perangkat.\n\n"
        "🛠️ *Cara Menggunakan:*\n"
        "1. Gunakan perintah `/generate_license` untuk membuat lisensi.\n"
        "2. Gunakan perintah `/verify_license <license_key>` untuk memverifikasi lisensi Anda.\n"
        "3. Gunakan perintah `/device_info` untuk melihat informasi perangkat Anda.\n\n"
        "📞 *Informasi Kontak:*\n"
        f"Nama: Fanky\n"
        f"Email: radenmanis123@gmail.com\n"
        f"Telepon: 0895359611122\n\n"
        "🌐 *Media Sosial:*\n"
        "Website: [fankyxd.xyz](https://fankyxd.xyz)\n"
        "Instagram: [@fannjha](https://instagram.com/fannjha)\n"
        "GitHub: [fanky86](https://github.com/fanky86)\n"
        "Telegram: [@fankyxd](t.me/fankyxd)\n\n"
        "Selamat mencoba dan hubungi saya jika ada pertanyaan! 😊"
    )
    bot.reply_to(message, welcome_message, parse_mode="Markdown")

# Command /generate_license
@bot.message_handler(commands=['generate_license'])
def generate_license(message):
    user_id = message.chat.id

    # Cek apakah lisensi sudah pernah dibuat untuk perangkat ini
    if user_id in licenses:
        bot.reply_to(
            message,
            f"Anda sudah memiliki lisensi: `{licenses[user_id]}`\nLisensi tidak dapat diubah.",
            parse_mode="Markdown"
        )
        return

    # Jika belum ada lisensi, buat lisensi baru
    license_key = str(uuid.uuid4())
    licenses[user_id] = license_key
    bot.reply_to(
        message,
        f"Lisensi baru berhasil dibuat untuk perangkat Anda: `{license_key}`",
        parse_mode="Markdown"
    )

# Command /verify_license
@bot.message_handler(commands=['verify_license'])
def verify_license(message):
    user_id = message.chat.id
    license_key = message.text.split()[-1]

    # Validasi lisensi berdasarkan user_id
    if licenses.get(user_id) == license_key:
        bot.reply_to(message, "✅ Lisensi Anda valid!")
    else:
        bot.reply_to(message, "❌ Lisensi tidak valid atau tidak terdaftar untuk perangkat ini.")

# Command /device_info
@bot.message_handler(commands=['device_info'])
def device_info(message):
    system_info = platform.uname()
    response = (
        f"**Device Info:**\n"
        f"- System: {system_info.system}\n"
        f"- Node: {system_info.node}\n"
        f"- Release: {system_info.release}\n"
        f"- Version: {system_info.version}\n"
        f"- Machine: {system_info.machine}\n"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

# Webhook untuk Vercel
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# Set Webhook
@app.route("/")
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://bottelegram-five.vercel.app/{TOKEN}")
    return "Bot is running!, bot ku https://t.me/Licensi_fan_bot", 200

if __name__ == "__main__":
    app.run(debug=True)
