import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from flask import Flask, request

app = Flask(__name__)

# Token Bot Telegram
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Fungsi untuk menampilkan tombol inline
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Tombol 1", callback_data='button1')],
        [InlineKeyboardButton("Tombol 2", callback_data='button2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Pilih tombol di bawah ini:', reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ketik /start untuk memulai dan melihat tombol.')

# Fungsi untuk menangani tombol yang ditekan
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # Mengirimkan balasan berdasarkan tombol yang dipilih
    if query.data == 'button1':
        query.edit_message_text(text="Anda memilih Tombol 1!")
    elif query.data == 'button2':
        query.edit_message_text(text="Anda memilih Tombol 2!")

# Inisialisasi Updater dan Dispatcher
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# Menambahkan handler untuk perintah dan tombol
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CallbackQueryHandler(button))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), updater.bot)
    dp.process_update(update)
    return '', 200

@app.route('/')
def index():
    return 'Bot is running!'

# Fungsi untuk mengatur webhook
def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL') + TOKEN
    updater.bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    # Set webhook saat menjalankan aplikasi secara lokal atau di Vercel
    set_webhook()
    app.run(debug=True)
