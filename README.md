# 🤖 Discord Bot (Multipurpose Management & Moderation Bot)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python ve `discord.py` ile geliştirilmiş, modüler mimariye sahip gelişmiş **Discord Sunucu Yönetim, Moderasyon, Güvenlik, Seviye, Çekiliş ve Karşılama Botu**.

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

## 🚀 Kurulum ve Çalıştırma

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
