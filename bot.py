import telebot
import platform
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
    welcome_message = (
        f"Selamat datang, {message.from_user.first_name}!\n\n"
        "📌 *Tentang Bot Ini:*\n"
        "Bot ini digunakan untuk memverifikasi lisensi script Python Anda dan memberikan informasi perangkat.\n\n"
        "🛠️ *Cara Menggunakan:*\n"
        "1. Gunakan perintah `/generate_license` untuk membuat lisensi.\n"
        "2. Gunakan perintah `/verify_license <license_key>` untuk memverifikasi lisensi Anda.\n"
        "3. Gunakan perintah `/device_info` untuk melihat informasi perangkat Anda.\n"
        "4. Gunakan perintah `/set_expiry <license_key> <hari>` untuk mengubah tanggal kedaluwarsa lisensi (Admin saja).\n\n"
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
            f"Anda sudah memiliki lisensi: `{licenses[user_id]['key']}`\n"
            f"📅 Dibuat pada: `{licenses[user_id]['created_at']}`\n"
            f"⏳ Kedaluwarsa: `{licenses[user_id]['expires_at']}`",
            parse_mode="Markdown"
        )
        return

    # Jika belum ada lisensi, buat lisensi baru
    license_key = str(uuid.uuid4())
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=30)  # Default masa aktif 30 hari

    # Simpan lisensi
    licenses[user_id] = {
        "key": license_key,
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }

    bot.reply_to(
        message,
        f"Lisensi baru berhasil dibuat untuk perangkat Anda:\n"
        f"🔑 Lisensi: `{license_key}`\n"
        f"📅 Dibuat pada: `{licenses[user_id]['created_at']}`\n"
        f"⏳ Kedaluwarsa: `{licenses[user_id]['expires_at']}`",
        parse_mode="Markdown"
    )

# Command /verify_license
@bot.message_handler(commands=['verify_license'])
def verify_license(message):
    user_id = message.chat.id
    try:
        license_key = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Format salah. Gunakan format: `/verify_license <license_key>`", parse_mode="Markdown")
        return

    # Validasi lisensi berdasarkan user_id
    if user_id in licenses and licenses[user_id]["key"] == license_key:
        expires_at = datetime.strptime(licenses[user_id]["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_at:
            bot.reply_to(message, "❌ Lisensi Anda telah kedaluwarsa.")
        else:
            bot.reply_to(message, "✅ Lisensi Anda valid!")
    else:
        bot.reply_to(message, "❌ Lisensi tidak valid atau tidak terdaftar untuk perangkat ini.")

# Command /set_expiry (Admin)
@bot.message_handler(commands=['set_expiry'])
def set_expiry(message):
    try:
        _, license_key, days = message.text.split()
        days = int(days)

        # Cari lisensi berdasarkan key
        for user_id, license_data in licenses.items():
            if license_data["key"] == license_key:
                new_expiry = datetime.now() + timedelta(days=days)
                licenses[user_id]["expires_at"] = new_expiry.strftime("%Y-%m-%d %H:%M:%S")
                bot.reply_to(
                    message,
                    f"⏳ Tanggal kedaluwarsa lisensi `{license_key}` berhasil diperbarui:\n"
                    f"📅 Baru: `{licenses[user_id]['expires_at']}`",
                    parse_mode="Markdown"
                )
                return

        bot.reply_to(message, "❌ Lisensi tidak ditemukan.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Format salah. Gunakan format: `/set_expiry <license_key> <hari>`", parse_mode="Markdown")

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
