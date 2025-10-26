# 🤖 Discord Bot dengan Gemini AI & Game System

Bot Discord yang dilengkapi dengan AI Gemini untuk chat, sistem game untuk mengumpulkan poin, dan fitur VIP eksklusif!

## ✨ Fitur

### 🎮 Game & Points System
- 💰 **Daily Rewards**: Klaim poin setiap hari
- 🎯 **Mini Games**: Main game untuk dapat poin
- 🏆 **Leaderboard**: Kompetisi pemain top
- 💾 **Persistent Data**: Points tersimpan di JSON, tidak hilang saat bot restart

### 👑 VIP System
- 🛒 **Shop**: Beli VIP dengan poin yang dikumpulkan
- 🎨 **Buat Sticker**: VIP bisa buat custom sticker untuk server
- 😀 **Buat Emoji**: VIP bisa buat custom emoji untuk server
- 🔊 **Upload Soundboard**: VIP bisa upload audio soundboard

### 💬 AI Chat
- 💬 **Q&A dengan Gemini AI**: Tanya apa saja di server (mention bot)
- 🤖 **DM Chat dengan Personality**: Chat pribadi dengan bot yang memiliki identitas custom
- 💾 **Per-User Memory**: Setiap user memiliki bot identity dan riwayat chat tersendiri
- 🎭 **Custom Bot Identity**: Tentukan nama dan personality bot sesuai keinginan
- ⚡ **Async**: Menggunakan asynchronous programming untuk performa optimal

## 📋 Prasyarat

1. **Python 3.8+** terinstall di sistem Anda
2. **Discord Bot Token** - Buat bot di [Discord Developer Portal](https://discord.com/developers/applications)
3. **Gemini API Key** - Dapatkan dari [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🚀 Instalasi

### 1. Clone atau Download Repository

```bash
cd "e:\Website python\Bot-discord"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables

1. Salin file `.env.example` menjadi `.env`:
```bash
copy .env.example .env
```

2. Edit file `.env` dan isi dengan kredensial Anda:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Setup Discord Bot

1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. Klik "New Application" dan beri nama
3. Pergi ke tab "Bot" dan klik "Add Bot"
4. Di bagian "Privileged Gateway Intents", aktifkan:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (optional)
5. Salin token bot Anda dan masukkan ke `.env`

### 5. Invite Bot ke Server

Gunakan URL berikut (ganti `YOUR_CLIENT_ID` dengan Client ID bot Anda):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274878024768&scope=bot
```

**Permissions yang dibutuhkan:**
- Read Messages/View Channels
- Send Messages
- Manage Emojis and Stickers (untuk VIP features)
- Attach Files
- Use External Emojis

## 🎮 Cara Menggunakan

### Menjalankan Bot

```bash
python bot.py
```

Jika berhasil, Anda akan melihat pesan:
```
[Bot Name] telah online!
Bot ID: [Bot ID]
Bot siap digunakan!
```

### Perintah Bot

#### 🎮 Game & Points Commands

```
!daily - Klaim daily reward (100 points)
!game - Main mini game tebak angka
!points - Cek points dan VIP status kamu
!leaderboard - Lihat top 10 players
```

#### 👑 VIP Commands

```
!shop - Lihat shop dan harga VIP
!buyvip - Beli VIP status (10,000 points)
!vip - Cek VIP status kamu
```

#### ✨ VIP-Only Features

**Buat Sticker**
```
!sticker
```
- Upload gambar (PNG/JPG/GIF)
- Berikan nama sticker
- Bot akan membuat sticker untuk server

**Buat Emoji**
```
!emoji
```
- Upload gambar (PNG/JPG/GIF, max 256KB)
- Berikan nama emoji
- Bot akan membuat emoji untuk server

**Upload Soundboard**
```
!soundboard
```
- Upload file audio (MP3/WAV/OGG/M4A, max 5MB)
- File akan disimpan di server
- Lihat list dengan `!listsounds`

#### 📢 Di Server (Mention Bot)

Bot hanya merespons ketika **di-mention/tag**.

**1. Bertanya pada Gemini AI**
```
@BotName Apa itu Python?
@BotName Jelaskan tentang AI
@BotName Bagaimana cara membuat bot Discord?
```

**2. Command Server**
```
!help - Menampilkan panduan penggunaan
!ping - Mengecek latency bot
!dmhelp - Panduan fitur DM chat
```

#### 💬 Di DM (Direct Message)

**1. Setup Bot Identity (Wajib sebelum chat)**
```
/setup nama: Luna
personality: Kamu adalah asisten AI yang ramah, ceria, dan suka membantu. Kamu berbicara dengan gaya santai tapi sopan, dan suka menggunakan emoji. Kamu sangat tertarik dengan teknologi dan seni.
```

**Contoh Setup Lainnya:**
```
/setup nama: Stark
personality: Kamu adalah AI genius seperti Tony Stark, sarkastik tapi pintar, suka teknologi dan sains.
```

```
/setup nama: Miko
personality: Kamu adalah AI kawaii dari Jepang, selalu ceria dan suka anime. Kamu sering pakai emoticon (^_^).
```

**2. Chat dengan Bot**

Setelah setup, langsung kirim pesan apa saja:
```
Halo! Apa kabar?
Ceritakan tentang AI
Bantu aku belajar Python dong
```

Bot akan merespons sesuai personality yang kamu berikan!

**3. Command DM**
```
/reset - Hapus riwayat chat (mulai percakapan baru)
/identity - Lihat bot identity dan statistik
/setup - Ubah nama dan personality bot
```

## 📁 Struktur File

```
Bot-discord/
├── bot.py                      # File utama bot
├── .env                        # File konfigurasi (JANGAN share!)
├── .env.example                # Template konfigurasi
├── requirements.txt            # Dependencies Python
├── README.md                   # Dokumentasi (file ini)
└── user_data/                  # Data user (auto-generated)
    ├── bot_identities.json     # Identity bot per user
    ├── user_points.json        # Points setiap user
    ├── user_vip.json          # Status VIP setiap user
    ├── daily_claims.json      # Tracking daily claim
    ├── chat_history/          # Folder riwayat chat
    │   ├── [user_id_1].json   # Chat history user 1
    │   └── [user_id_2].json   # Chat history user 2
    ├── stickers/              # Sticker files (VIP)
    ├── emojis/                # Emoji files (VIP)
    └── soundboards/           # Audio soundboard files (VIP)
```

## 🔧 Troubleshooting

### Bot tidak merespons di server
- Pastikan MESSAGE CONTENT INTENT sudah diaktifkan di Discord Developer Portal
- Cek apakah bot sudah online dengan command `!ping`
- Pastikan Anda men-tag/mention bot dengan benar

### Bot tidak merespons di DM
- Pastikan Anda sudah setup bot identity dengan `/setup`
- Cek folder `user_data` sudah terbuat otomatis
- Pastikan bot memiliki permission untuk kirim DM

### VIP features tidak bisa digunakan
- Pastikan sudah beli VIP dengan `!buyvip`
- Cek VIP status dengan `!vip`
- Untuk sticker/emoji, user harus punya permission "Manage Emojis and Stickers" di server

### Points tidak tersimpan
- Jangan hapus file `user_data/user_points.json`
- Backup folder `user_data` secara berkala

### Error Gemini API
- Cek apakah GEMINI_API_KEY sudah benar
- Pastikan API key masih aktif di [Google AI Studio](https://makersuite.google.com/app/apikey)

### Chat history atau identity hilang
- Jangan hapus folder `user_data`
- Backup folder `user_data` secara berkala
- Setiap user memiliki file terpisah berdasarkan Discord user ID

## 📝 Catatan

- Bot ini menggunakan **Gemini 2.0 Flash** untuk text generation
- Discord memiliki batas 2000 karakter per pesan, jawaban panjang akan dipecah otomatis
- Free tier Gemini API memiliki limit request per menit
- **VIP Price**: 10,000 points
- **Daily Reward**: 100 points
- **Game Reward**: 10-50 points
- **DM Chat Features:**
  - Setiap user punya bot identity dan chat history sendiri
  - Chat history disimpan hingga 50 pesan terakhir (otomatis)
  - Bot akan merespons sesuai personality yang diberikan
  - Data disimpan lokal di folder `user_data`
- **Data Persistence**: Semua data (points, VIP, chat) tersimpan di JSON files

## 🛡️ Keamanan

⚠️ **PENTING**: Jangan pernah share file `.env` atau upload ke repository public!

File `.env` berisi kredensial sensitif yang bisa disalahgunakan.

## 📄 License

Silakan digunakan dan dimodifikasi sesuai kebutuhan.

## 🤝 Kontribusi

Feel free to fork dan melakukan improvement pada bot ini!

---

**Selamat menggunakan! 🎉**
