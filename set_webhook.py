import requests

# Ganti dengan token Telegram Bot Anda
TELEGRAM_TOKEN = '7829625950:AAHAkDANqB9yalb2vClpxX5zXBpHBaq_iVM'

# Ganti dengan URL webhook aplikasi yang sudah dideploy di Vercel
WEBHOOK_URL = 'https://bottelegram-two.vercel.app/webhook'  # URL aplikasi Anda di Vercel

# Mengatur webhook Telegram
url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'

response = requests.get(url)

# Cek apakah webhook berhasil diset
print(response.json())
