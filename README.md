# 🤖 Discord Bot (Multipurpose Management & Moderation Bot)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python ve `discord.py` ile geliştirilmiş, modüler mimariye sahip gelişmiş **Discord Sunucu Yönetim, Moderasyon, Güvenlik, Seviye, Çekiliş ve Karşılama Botu**.

Dahili **Flask Web Sunucusu (Keep-Alive)** desteği sayesinde **Replit** ve **UptimeRobot** ile 7/24 kesintisiz çalıştırılabilir.

---

## 🌟 Bot Özellikleri

- 🛡️ **Güvenlik & Auto-Mod**: Spam koruması, büyük harf (caps) filtresi, küfür engeli, reklam/link engeli ve beyaz liste (whitelist) yönetimi.
- 🔨 **Moderasyon Komutları**: Üye yasaklama (`/ban`), yasa kaldırma (`/unban`), atma (`/kick`), susturma (`/mute`), susturma kaldırma (`/unmute`), uyarı sistemi (`/uyar`, `/uyarılar`, `/uyarisil`), kanal kilitleme (`/kilitle`), yavaş mod (`/yavaslat`) ve mesaj temizleme (`/temizle`).
- 📈 **Seviye (Leveling) Sistemi**: Mesaj gönderdikçe XP kazanma, seviye kartı görüntüleme (`/rank`), seviyeye özel otomatik rol ödülleri ve özelleştirilebilir bildirim kanalı.
- 👋 **Karşılama (Welcome) Sistemi**: Sunucuya yeni katılan ve ayrılan üyeler için özelleştirilebilir karşılama/görüşürüz mesajları ve kanalı.
- 🎉 **Çekiliş (Giveaway) Sistemi**: Süreli, ödüllü ve butonlu çekiliş başlatma ve otomatik kazanan seçimi (`/çekiliş-başlat`).
- ⚙️ **İnteraktif Kontrol Paneli**: Butonlu ve açılır menülü gelişmiş sunucu yönetim paneli (`/panel` veya `c!panel`).
- 🔊 **Ses Kanalı Koruması**: Botun belirlenen ses kanalında 7/24 kesintisiz aktif kalması ve otomatik yeniden bağlanma (`/sesegir`, `/sestenayril`).
- 💬 **Kelime Filtresi**: Sunucuya özel yasaklı kelime listesi yönetimi (`c!kelimeekle`, `c!kelimesil`, `c!kelimeler`, `c!kelimetemizle`).
- 🎲 **Eğlence ve Araçlar**: `/espiri`, `/yazıtura`, `/ping`, `/avatar`, `/kb`, `/sb`.

---

## 🌐 Replit & UptimeRobot ile 7/24 Ücretsiz Deploy (Hosting)

Botun içerisinde dahili **Flask Keep-Alive** sunucusu entegrelidir. Aşağıdaki adımları izleyerek botu bilgisayarınızı açık tutmadan 7/24 çalıştırabilirsiniz:

### 1️⃣ Replit Kurulumu:
1. [Replit.com](https://replit.com) sitesine giriş yapın.
2. **Create Repl** ➔ **Import from GitHub** seçeneğine tıklayın.
3. URL alanına `https://github.com/favianan/Discord-Bot` yazıp repoyu aktarın.
4. Sol menüden **Tools ➔ Secrets** (Kilit simgesi) sekmesini açın:
   - **Key:** `BOT_TOKEN`
   - **Value:** `Discord Bot Tokeniniz`
   - **Add Secret** butonuna tıklayın.
5. Üstteki **Run** butonuna basarak botu başlatın.
6. Sağ üst taraftaki **Webview** penceresinde oluşan web adresini kopyalayın (Örn: `https://discord-bot.kullaniciadi.repl.co`).

### 2️⃣ UptimeRobot ile 7/24 Aktif Tutma:
1. [UptimeRobot.com](https://uptimerobot.com) adresine ücretsiz kaydolun.
2. **Add New Monitor** butonuna tıklayın:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Discord Bot 7/24`
   - **URL (or IP):** Replit'te kopyaladığınız Webview adresini yapıştırın.
   - **Monitoring Interval:** `5 minutes` (5 dakikada bir)
3. **Create Monitor** butonuna basın. Botunuz 7/24 kapanmadan çalışacaktır!

---

## 💻 Yerel (Local) Kurulum

1. **Repoyu İndirin:**
   ```bash
   git clone https://github.com/favianan/Discord-Bot.git
   cd Discord-Bot
   ```

2. **Gerekli Kütüphaneleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Botu Çalıştırın:**
   ```bash
   # Windows (PowerShell)
   $env:BOT_TOKEN="SENIN_BOT_TOKENIN"
   python main.py

   # Linux / macOS
   export BOT_TOKEN="SENIN_BOT_TOKENIN"
   python main.py
   ```

---

## ⚙️ Prefix ve Yapılandırma

- **Prefix Değiştirme**: `main.py` dosyasında yer alan `command_prefix="c!"` alanından botun prefix'ini değiştirebilirsiniz (Örn: `!`, `.`, `?`).
- **Yardım Menüsü**: Bot içerisinden `/yardım` veya `c!yardım` yazarak interaktif yardım menüsünü kullanabilirsiniz.

---

## 📄 Lisans

MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.

Geliştirici: **Yusuf Cebeci @58tc**
