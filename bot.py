import os
import openai
from flask import Flask, request
from telegram import Bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Set API key OpenAI dan token Telegram Anda
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Pastikan API key OpenAI sudah diset di Vercel
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Pastikan token bot Telegram sudah diset di Vercel

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

# Fungsi untuk menangani pesan dengan menggunakan aplikasi Telegram
async def start(update: Update, context):
    await update.message.reply_text("Hi! Send me a message and I'll reply using AI.")

# Menambahkan handler untuk teks
async def handle_message(update: Update, context):
    user_message = update.message.text
    ai_response = get_ai_response(user_message)
    await update.message.reply_text(ai_response)

# Menjalankan Flask app
if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Menambahkan handler untuk start dan pesan teks
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook route di Flask
    app.run(debug=True)
