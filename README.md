# 🤖 Discord Bot (Multipurpose Management & Moderation Bot)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python ve `discord.py` ile geliştirilmiş, modüler mimariye sahip gelişmiş **Discord Sunucu Yönetim, Moderasyon, Güvenlik, Seviye, Çekiliş ve Karşılama Botu**.

Dahili **Flask Web Sunucusu (Keep-Alive)** desteği sayesinde **AWS EC2**, **Replit**, **Render** ve **UptimeRobot** ile 7/24 kesintisiz çalıştırılabilir.

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

## ☁️ AWS EC2 ile 7/24 Deploy (1 Yıl Ücretsiz VPS)

AWS (Amazon Web Services) **Free Tier (1 Yıl Ücretsiz)** kapsamında sunulan Ubuntu EC2 sunucusu ile botunuzu 7/24 sıfır kesintiyle çalıştırabilirsiniz:

### 1️⃣ EC2 Sunucusu Oluşturma:
1. AWS Console ➔ **EC2** ➔ **Launch Instance** butonuna tıklayın.
2. Sunucu Adı: `Discord-Bot`
3. İşletim Sistemi (AMI): **Ubuntu 24.04 LTS / 22.04 LTS**
4. Sunucu Tipi: **t2.micro** veya **t3.micro** (Free tier eligible)
5. **Key Pair (Anahtar Çifti)**: `.pem` anahtar dosyasını indirin.
6. **Launch Instance** butonuna basarak sunucuyu başlatın.

### 2️⃣ SSH ile Bağlanma ve Botu Kurma:
```bash
# SSH ile sunucuya bağlanın (Windows PowerShell veya Terminal)
ssh -i "keyiniz.pem" ubuntu@SUNUCU_IP_ADRESI

# Sistem paketlerini güncelleyin ve Git & Python yükleyin
sudo apt update && sudo apt install -y python3 python3-pip git

# Repoyu klonlayın ve klasöre girin
git clone https://github.com/favianan/Discord-Bot.git
cd Discord-Bot

# Bağımlılıkları yükleyin
pip3 install -r requirements.txt
```

### 3️⃣ Systemd Servisi Oluşturup 7/24 Arka Planda Çalıştırma:
Botun sunucu kapansanız/yeniden başlasa bile otomatik başlaması için bir systemd servisi yazalım:

```bash
# Servis dosyasını oluşturun
sudo nano /etc/systemd/system/discordbot.service
```

Aşağıdaki içeriği yapıştırın (`TOKENINIZ` kısmına bot tokeninizi yazın):
```ini
[Unit]
Description=Discord Bot Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Discord-Bot
ExecStart=/usr/bin/python3 main.py
Environment="BOT_TOKEN=TOKENINIZ"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kaydedip çıkın (`Ctrl+O`, `Enter`, `Ctrl+X`). Servisi başlatın:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discordbot
sudo systemctl start discordbot

# Servis durumunu kontrol edin
sudo systemctl status discordbot
```

---

## 🌐 Replit & UptimeRobot ile 7/24 Ücretsiz Deploy

Botun içerisinde dahili **Flask Keep-Alive** sunucusu entegrelidir. Replit ve UptimeRobot kullanarak da 7/24 çalıştırabilirsiniz:

### 1️⃣ Replit Kurulumu:
1. [Replit.com](https://replit.com) sitesine giriş yapın.
2. **Create Repl** ➔ **Import from GitHub** seçeneğine tıklayın.
3. URL alanına `https://github.com/favianan/Discord-Bot` yazıp repoyu aktarın.
4. Sol menüden **Tools ➔ Secrets** (Kilit simgesi) sekmesini açın:
   - **Key:** `BOT_TOKEN`
   - **Value:** `Discord Bot Tokeniniz`
5. **Run** butonuna basın ve sağ üstteki Webview URL'sini kopyalayın.

### 2️⃣ UptimeRobot ile 7/24 Aktif Tutma:
1. [UptimeRobot.com](https://uptimerobot.com) adresinde **Add New Monitor** deyin:
   - **Monitor Type:** `HTTP(s)`
   - **URL:** Replit Webview URL'niz
   - **Interval:** `5 minutes`
2. **Create Monitor** diyerek 7/24 aktif edin.

---

## 💻 Yerel (Local) Kurulum

```bash
git clone https://github.com/favianan/Discord-Bot.git
cd Discord-Bot
pip install -r requirements.txt

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
