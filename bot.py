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
    bot.reply_to(
        message,
        f"Selamat datang {message.from_user.first_name}! "
        "Gunakan bot ini untuk memverifikasi lisensi script Python Anda."
    )

# Command /generate_license
@bot.message_handler(commands=['generate_license'])
def generate_license(message):
    user_id = message.chat.id
    license_key = str(uuid.uuid4())
    licenses[user_id] = license_key
    bot.reply_to(message, f"Lisensi Anda: `{license_key}`", parse_mode="Markdown")

# Command /verify_license
@bot.message_handler(commands=['verify_license'])
def verify_license(message):
    user_id = message.chat.id
    license_key = message.text.split()[-1]
    if licenses.get(user_id) == license_key:
        bot.reply_to(message, "Lisensi valid! 🚀")
    else:
        bot.reply_to(message, "Lisensi tidak valid atau sudah digunakan.")

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
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=True)
