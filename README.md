# 🤖 Gelişmiş Discord Botu (Multipurpose Bot & Server Cloner)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python ve `discord.py` ile geliştirilmiş, kapsamlı **Moderasyon, Güvenlik, Seviye, Çekiliş, Karşılama ve Sunucu Klonlama** özelliklerine sahip gelişmiş bir Discord botu projesidir.

---

## 🌟 Bot Özellikleri (`main.py`)

- 🛡️ **Güvenlik & Auto-Mod**: Spam koruması, büyük harf (caps) engeli, küfür filtresi, reklam/link engeli ve beyaz liste (whitelist) sistemi.
- 🔨 **Gelişmiş Moderasyon**: `/ban`, `/unban`, `/kick`, `/mute`, `/unmute`, `/uyar`, `/uyarılar`, `/temizle`, `/kilitle`, `/yavaslat` komutları.
- 📈 **Seviye (Leveling) Sistemi**: Mesaj attıkça tecrübe puanı (XP) kazanma, seviye atlama kartları (`/rank`), seviyeye özel otomatik rol ödülleri.
- 👋 **Karşılama (Welcome) Sistemi**: Sunucuya giren ve çıkan üyeler için özelleştirilebilir resimli/metinli karşılama mesajları.
- 🎉 **Çekiliş (Giveaway) Sistemi**: Butonlu ve süreli gelişmiş çekiliş başlatma ve otomatik kazanan seçme.
- ⚙️ **İnteraktif Kontrol Paneli**: Butonlu ve menülü gelişmiş sunucu yönetim paneli (`c!panel` / `/panel`).
- 🔊 **Ses Kanalı Koruması**: Botun ses kanalında kesintisiz aktif kalması ve otomatik yeniden bağlanma (`/sesegir`).
- 💬 **Kelime Filtresi**: Sunucuya özel yasaklı kelime ekleme/çıkarma ve otomatik temizleme.
- 🛠️ **Sunucu Klonlama (`Cloner.py`)**: Roller, kanallar, kategoriler, emojiler ve çıkartmaları birebir kopyalama aracı.

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

3. **Botu Çalıştırın (`main.py`):**
   ```bash
   # Windows (PowerShell)
   $env:BOT_TOKEN="BOT_TOKENINIZ"
   python main.py

   # Linux / macOS
   export BOT_TOKEN="YOUR_BOT_TOKEN"
   python main.py
   ```

4. **Sunucu Klonlama Aracını Çalıştırın (`Cloner.py`):**
   ```bash
   python Cloner.py
   ```

---

## ⚙️ Prefix ve Yapılandırma

- **Prefix Değiştirme**: `main.py` dosyasındaki `command_prefix="c!"` kısmından botun prefix'ini değiştirebilirsiniz (Örn: `!`, `.`, `?`).
- **Yardım Menüsü**: Bot içerisinden `/yardım` veya `c!yardım` komutu ile interaktif yardım menüsüne ulaşabilirsiniz.

---

## 📄 Lisans

MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.

Geliştirici: **Yusuf Cebeci @58tc**
