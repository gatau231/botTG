import requests

# Ganti dengan token Telegram Bot Anda
TELEGRAM_TOKEN = '7829625950:AAHAkDANqB9yalb2vClpxX5zXBpHBaq_iVM'

# Ganti dengan URL webhook aplikasi yang sudah dideploy di Vercel
WEBHOOK_URL = 'https://<your-vercel-app>.vercel.app/webhook'  # URL Vercel Anda

# Mengatur webhook Telegram
url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'

response = requests.get(url)

# Cek apakah webhook berhasil diset
print(response.json())
