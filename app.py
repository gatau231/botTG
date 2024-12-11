import os
import sqlite3
from datetime import datetime
from flask import Flask, request
import telebot

# Token bot Telegram
BOT_TOKEN = "7775657017:AAFUqZqsuMB5NSfTrUPDWx6TW2hcEfSOeT0"
bot = telebot.TeleBot(BOT_TOKEN)

# URL server (akan otomatis diisi dengan URL Vercel/Heroku)
APP_URL = f"https://{os.getenv('VERCEL_URL')}/{BOT_TOKEN}"

# Inisialisasi Flask untuk Webhook
app = Flask(__name__)

# Fungsi untuk inisialisasi database
def init_db():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE,
            status TEXT DEFAULT 'inactive',
            activated_by TEXT,
            activation_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Aktivasi lisensi
@bot.message_handler(commands=["activate"])
def activate_license(message):
    try:
        user_id = message.chat.id
        license_key = message.text.split(" ", 1)[1].strip()  # Lisensi dari user
        conn = sqlite3.connect("licenses.db")
        cursor = conn.cursor()

        # Cek lisensi di database
        cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
        license_data = cursor.fetchone()

        if not license_data:
            bot.reply_to(message, "❌ Lisensi tidak valid.")
        elif license_data[2] == "active":
            bot.reply_to(message, f"⚠️ Lisensi sudah aktif oleh user ID: {license_data[3]}")
        else:
            # Aktivasi lisensi
            activation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE licenses SET status = 'active', activated_by = ?, activation_date = ? WHERE license_key = ?",
                (user_id, activation_date, license_key),
            )
            conn.commit()
            bot.reply_to(message, f"✅ Lisensi {license_key} berhasil diaktifkan!")
        conn.close()
    except IndexError:
        bot.reply_to(message, "⚠️ Gunakan format: /activate <license_key>")
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan: {e}")

# Mengecek status lisensi
@bot.message_handler(commands=["check"])
def check_license(message):
    try:
        license_key = message.text.split(" ", 1)[1].strip()
        conn = sqlite3.connect("licenses.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
        license_data = cursor.fetchone()

        if not license_data:
            bot.reply_to(message, "❌ Lisensi tidak ditemukan.")
        else:
            status = license_data[2]
            activated_by = license_data[3] or "Belum diaktifkan"
            activation_date = license_data[4] or "Belum diaktifkan"
            bot.reply_to(
                message,
                f"🔍 Status Lisensi:\n"
                f"Key: {license_key}\n"
                f"Status: {status}\n"
                f"Diaktifkan oleh: {activated_by}\n"
                f"Tanggal Aktivasi: {activation_date}",
            )
        conn.close()
    except IndexError:
        bot.reply_to(message, "⚠️ Gunakan format: /check <license_key>")
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan: {e}")

# Nonaktifkan lisensi
@bot.message_handler(commands=["deactivate"])
def deactivate_license(message):
    try:
        license_key = message.text.split(" ", 1)[1].strip()
        conn = sqlite3.connect("licenses.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
        license_data = cursor.fetchone()

        if not license_data:
            bot.reply_to(message, "❌ Lisensi tidak ditemukan.")
        elif license_data[2] == "inactive":
            bot.reply_to(message, "⚠️ Lisensi sudah tidak aktif.")
        else:
            cursor.execute(
                "UPDATE licenses SET status = 'inactive', activated_by = NULL, activation_date = NULL WHERE license_key = ?",
                (license_key,),
            )
            conn.commit()
            bot.reply_to(message, f"✅ Lisensi {license_key} berhasil dinonaktifkan.")
        conn.close()
    except IndexError:
        bot.reply_to(message, "⚠️ Gunakan format: /deactivate <license_key>")
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan: {e}")

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    json_update = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "!", 200

# Route untuk pengecekan status
@app.route("/", methods=["GET"])
def home():
    return "Bot Telegram Aktif!", 200

# Jalankan Webhook
if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
