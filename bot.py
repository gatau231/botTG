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
    welcome_message = f"""
Selamat datang, {message.from_user.first_name}!

📌 *Tentang Bot Ini:*
Bot ini digunakan untuk memverifikasi lisensi script Python Anda dan memberikan informasi perangkat.

🛠️ *Cara Menggunakan:*
1. Gunakan perintah `/generate_license` untuk membuat lisensi.
2. Gunakan perintah `/verify_license <license_key>` untuk memverifikasi lisensi Anda.
3. Gunakan perintah `/device_info` untuk melihat informasi perangkat Anda.
4. Gunakan perintah `/set_expiry <license_key> <hari>` untuk mengubah tanggal kedaluwarsa lisensi (Admin saja).

📞 *Informasi Kontak:*
Nama: Fanky  
Email: radenmanis123@gmail.com  
Telepon: 0895359611122

🌐 *Media Sosial:*
- Website: [fankyxd.xyz](https://fankyxd.xyz)  
- Instagram: [@fannjha](https://instagram.com/fannjha)  
- GitHub: [fanky86](https://github.com/fanky86)  
- Telegram: [@fankyxd](https://t.me/fankyxd)

Selamat mencoba dan hubungi saya jika ada pertanyaan! 😊
"""
    bot.reply_to(message, welcome_message, parse_mode="Markdown")


# Command /generate_license
@bot.message_handler(commands=['generate_license'])
def generate_license(message):
    user_id = message.chat.id

    # Cek apakah lisensi sudah pernah dibuat
    if user_id in licenses:
        sent_message = bot.reply_to(
            message,
            f"Anda sudah memiliki lisensi: `{licenses[user_id]['key']}`\n"
            f"📅 Dibuat pada: `{licenses[user_id]['created_at']}`\n"
            f"⏳ Kedaluwarsa: `{licenses[user_id]['expires_at']}`",
            parse_mode="Markdown"
        )
        # Membaca pesan yang dikirim oleh bot
        read_message_from_bot(sent_message)
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

    sent_message = bot.reply_to(
        message,
        f"🔑 Lisensi berhasil dibuat:\n"
        f"Lisensi: `{license_key}`\n"
        f"Dibuat: `{licenses[user_id]['created_at']}`\n"
        f"Kedaluwarsa: `{licenses[user_id]['expires_at']}`",
        parse_mode="Markdown"
    )

    # Membaca kembali pesan yang dikirim oleh bot
    read_message_from_bot(sent_message)

# Fungsi untuk membaca pesan yang dikirim oleh bot
def read_message_from_bot(sent_message):
    # Mendapatkan detail pesan yang baru dikirim
    message_id = sent_message.message_id
    chat_id = sent_message.chat.id
    text = sent_message.text

    print(f"Pesan yang baru dikirim oleh bot:")
    print(f"Chat ID: {chat_id}")
    print(f"Message ID: {message_id}")
    print(f"Teks: {text}")

    # Jika diperlukan, tambahkan logika pemrosesan lebih lanjut di sini
    if "Lisensi berhasil dibuat" in text:
        print(f"Lisensi yang dibuat dan dikirim bot: {text}")


# Command /verify_license
@bot.message_handler(commands=['verify_license'])
def verify_license(message):
    try:
        license_key = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Gunakan format: `/verify_license <license_key>`", parse_mode="Markdown")
        return

    for user_id, license_data in licenses.items():
        if license_data["key"] == license_key:
            expires_at = datetime.strptime(license_data["expires_at"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expires_at:
                bot.reply_to(message, "❌ Lisensi Anda telah kedaluwarsa.")
            else:
                bot.reply_to(message, "✅ Lisensi valid!")
            return

    bot.reply_to(message, "❌ Lisensi tidak ditemukan.")

# Command /set_expiry
@bot.message_handler(commands=['set_expiry'])
def set_expiry(message):
    try:
        _, license_key, days = message.text.split()
        days = int(days)

        for user_id, license_data in licenses.items():
            if license_data["key"] == license_key:
                new_expiry = datetime.now() + timedelta(days=days)
                licenses[user_id]["expires_at"] = new_expiry.strftime("%Y-%m-%d %H:%M:%S")
                bot.reply_to(
                    message,
                    f"⏳ Kedaluwarsa lisensi diperbarui: `{licenses[user_id]['expires_at']}`",
                    parse_mode="Markdown"
                )
                return

        bot.reply_to(message, "❌ Lisensi tidak ditemukan.")
    except ValueError:
        bot.reply_to(message, "❌ Gunakan format: `/set_expiry <license_key> <hari>`", parse_mode="Markdown")

# Endpoint validasi lisensi untuk script premium
@app.route("/validate_license", methods=["POST"])
def validate_license():
    data = request.get_json()
    license_key = data.get("license_key")

    for user_id, license_data in licenses.items():
        if license_data["key"] == license_key:
            expires_at = datetime.strptime(license_data["expires_at"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expires_at:
                return {"status": "invalid", "message": "Lisensi telah kedaluwarsa."}
            return {"status": "valid", "message": "Lisensi valid."}

    return {"status": "invalid", "message": "Lisensi tidak ditemukan."}

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
