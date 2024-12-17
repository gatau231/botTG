import os
from flask import Flask, request
import openai
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Set API key OpenAI dan token Telegram Anda
openai.api_key = os.environ.get("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Inisialisasi bot Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# Inisialisasi Flask app
app = Flask(__name__)

# Fungsi untuk merespons pesan menggunakan OpenAI
def get_ai_response(user_message):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_message,
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Fungsi untuk menangani pesan masuk dari Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    chat_id = update["message"]["chat"]["id"]
    user_message = update["message"]["text"]
    
    ai_response = get_ai_response(user_message)
    
    # Kirim balasan ke pengguna
    bot.send_message(chat_id=chat_id, text=ai_response)
    
    return "OK", 200

# Menjalankan Flask app
if __name__ == "__main__":
    app.run(debug=True)
