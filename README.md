# 🚀 Discord Server Cloner & Multipurpose Bot

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A powerful, modular Discord tool set built with `discord.py` containing both a **Server Cloner Tool** and a **Multipurpose Management Bot** with interactive panels.

---

## 🌟 Key Features

### 🛠️ Server Cloner (`Cloner.py`)
- 🎭 **Role Cloning**: Preserves permissions, colors, hoist, and mentionable settings.
- 📁 **Channel & Category Cloning**: Replicates text/voice channels and categories with exact permission overwrites.
- 😀 **Emoji & Sticker Cloning**: Clones custom static/animated emojis and server stickers.
- 🎛️ **Modular Menu**: Choose full cloning or selectively clone roles, channels, emojis, or stickers.

### 🛡️ Multipurpose Bot (`main.py`)
- 🛡️ **Security & Moderation**: Auto-moderation (spam, caps, swear filter, link filter, whitelist) and moderation commands (`ban`, `kick`, `mute`, `warn`).
- 📈 **Leveling System**: XP system with custom notification channels and role rewards.
- 👋 **Welcome System**: Customizable join/leave messages and channels.
- 🎉 **Giveaways & Utility**: Interactive giveaways, help menu, ping, user/server info, and voice channel keep-alive.

---

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/favianan/Discord-Server-Cloner.git
   cd Discord-Server-Cloner
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 How to Use

### 1️⃣ Server Cloner Tool
Run the interactive cloner script:
```bash
python Cloner.py
```
Follow the CLI prompts:
1. Enter User Token / Bot Token
2. Enter Source Server ID
3. Enter Target Server ID
4. Select cloning options (1-7)

### 2️⃣ Multipurpose Bot
Set your bot token in your environment and run:
```bash
# Windows (PowerShell)
$env:BOT_TOKEN="YOUR_BOT_TOKEN"
python main.py

# Linux / macOS
export BOT_TOKEN="YOUR_BOT_TOKEN"
python main.py
```

---

## ⚙️ Configuration & Customization

- **Prefix**: Set in `main.py` (`command_prefix="c!"`). You can change `"c!"` to any prefix like `"!"` or `"."`.
- **Help Menu**: Accessible via `/yardım` or `c!yardım`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

Developed by **Yusuf Cebeci @58tc**
