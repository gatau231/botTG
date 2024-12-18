import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from flask import Flask, request

app = Flask(__name__)

# Token Bot Telegram
TOKEN = "7829625950:AAHAkDANqB9yalb2vClpxX5zXBpHBaq_iVM"  # Masukkan token bot Anda ke variabel lingkungan

# Fungsi untuk menangani perintah `/start`
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Tombol 1", callback_data='button1')],
        [InlineKeyboardButton("Tombol 2", callback_data='button2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Pilih tombol di bawah ini:', reply_markup=reply_markup)

# Fungsi untuk menangani perintah `/help`
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Ketik /start untuk memulai dan melihat tombol.')

# Fungsi untuk menangani klik tombol
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'button1':
        await query.edit_message_text(text="Anda memilih Tombol 1!")
    elif query.data == 'button2':
        await query.edit_message_text(text="Anda memilih Tombol 2!")

# Konfigurasi aplikasi Telegram
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Tambahkan handler untuk perintah dan tombol
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("help", help_command))
app_telegram.add_handler(CallbackQueryHandler(button))

@app.route('/' + TOKEN, methods=['POST'])
async def webhook():
    update_data = request.get_json()
    update = Update.de_json(update_data, app_telegram.bot)
    await app_telegram.process_update(update)
    return '', 200

@app.route('/')
def index():
    return 'Bot is running!'

# Fungsi untuk mengatur webhook
async def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL') + TOKEN  # URL webhook
    await app_telegram.bot.set_webhook(url=webhook_url)
    print(f"Webhook berhasil diatur: {webhook_url}")

if __name__ == '__main__':
    # Atur webhook sebelum menjalankan Flask
    import asyncio
    asyncio.run(set_webhook())
    app.run(debug=True)
