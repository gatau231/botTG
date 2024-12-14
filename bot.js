require("dotenv").config();
const TelegramBot = require("node-telegram-bot-api");
const express = require("express");
const os = require("os");
const { v4: uuidv4 } = require("uuid");

const TOKEN = process.env.TELEGRAM_API_TOKEN;
const bot = new TelegramBot(TOKEN, { polling: true });
const app = express();

// Dictionary untuk menyimpan lisensi per perangkat
const licenses = {}; // { userId: licenseKey }

// Command /start
bot.onText(/\/start/, (msg) => {
  const welcomeMessage = `
Selamat datang, ${msg.from.first_name}!

📌 *Tentang Bot Ini:*
Bot ini digunakan untuk memverifikasi lisensi script Python Anda dan memberikan informasi perangkat.

🛠️ *Cara Menggunakan:*
1. Gunakan perintah \`/generate_license\` untuk membuat lisensi (hanya 1 per perangkat).
2. Gunakan perintah \`/verify_license <license_key>\` untuk memverifikasi lisensi Anda.
3. Gunakan perintah \`/device_info\` untuk melihat informasi perangkat Anda.

📞 *Informasi Kontak:*
Nama: Fanky
Email: radenmanis123@gmail.com
Telepon: 0895359611122

🌐 *Media Sosial:*
Website: [fankyxd.xyz](https://fankyxd.xyz)
Instagram: [@fannjha](https://instagram.com/fannjha)
GitHub: [fankyxd](https://github.com/fanky86)

Telegram: [@fanky](t.me/fankyxd)
Selamat mencoba dan hubungi saya jika ada pertanyaan!
`;
  bot.sendMessage(msg.chat.id, welcomeMessage, { parse_mode: "Markdown" });
});

// Command /generate_license
bot.onText(/\/generate_license/, (msg) => {
  const userId = msg.chat.id;

  // Cek apakah perangkat sudah memiliki lisensi
  if (licenses[userId]) {
    bot.sendMessage(
      msg.chat.id,
      `Anda sudah memiliki lisensi: \`${licenses[userId]}\`. Lisensi tidak dapat diubah.`,
      { parse_mode: "Markdown" }
    );
    return;
  }

  // Buat lisensi baru untuk perangkat
  const licenseKey = uuidv4();
  licenses[userId] = licenseKey;

  bot.sendMessage(
    msg.chat.id,
    `Lisensi baru berhasil dibuat: \`${licenseKey}\``,
    { parse_mode: "Markdown" }
  );
});

// Command /verify_license
bot.onText(/\/verify_license (.+)/, (msg, match) => {
  const userId = msg.chat.id;
  const licenseKey = match[1]; // Ambil lisensi dari input user

  // Validasi lisensi
  if (licenses[userId] === licenseKey) {
    bot.sendMessage(msg.chat.id, "✅ Lisensi Anda valid!");
  } else {
    bot.sendMessage(msg.chat.id, "❌ Lisensi tidak valid atau tidak terdaftar untuk perangkat ini.");
  }
});

// Command /device_info
bot.onText(/\/device_info/, (msg) => {
  const systemInfo = {
    system: os.type(),
    release: os.release(),
    version: os.version(),
    machine: os.arch(),
    node: os.hostname(),
  };

  const response = `
**Device Info:**
- System: ${systemInfo.system}
- Node: ${systemInfo.node}
- Release: ${systemInfo.release}
- Version: ${systemInfo.version}
- Machine: ${systemInfo.machine}
`;
  bot.sendMessage(msg.chat.id, response, { parse_mode: "Markdown" });
});

// Webhook untuk Vercel
app.use(express.json());

app.post(`/${TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

// Endpoint untuk testing
app.get("/", (req, res) => {
  bot.setWebHook(`https://bottelegram-five.vercel.app/${TOKEN}`);
  res.send("Bot is running!");
});

// Jalankan server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server berjalan di port ${PORT}`);
});
