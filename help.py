import discord
from discord.ext import commands

COLOR = 0x2f3136

CATEGORIES = {
    "ana_sayfa": {
        "emoji": "🏠",
        "title": "Ana Sayfa",
        "description": "Aşağıdaki menüden bir kategori seçerek komutları listeleyebilirsiniz.",
    },
    "güvenlik": {
        "emoji": "🛡️",
        "title": "Güvenlik",
        "description": (
            "`/güvenlik` — Güvenlik sistemi kontrol panelini açar\n"
            "`/izinliekle <domain>` — Link filtresine istisna domain ekler\n"
            "`/izinlisil <domain>` — İstisna domain kaydını siler\n"
            "`/logkanali #kanal` — Güvenlik loglarının gönderileceği kanalı belirler"
        ),
    },
    "moderasyon": {
        "emoji": "🔨",
        "title": "Moderasyon",
        "description": (
            "`/ban @üye [sebep]` — Üyeyi sunucudan kalıcı olarak yasaklar\n"
            "`/unban <id/tag>` — Belirtilen üyenin yasağını kaldırır\n"
            "`/kick @üye [sebep]` — Üyeyi sunucudan atar\n"
            "`/mute @üye [süre] [sebep]` — Üyeyi susturur (Örn: 10m, 2h, 1d)\n"
            "`/unmute @üye` — Üyenin susturmasını kaldırır\n"
            "`/uyar @üye [sebep]` — Üyeye uyarı puanı ekler\n"
            "`/uyarılar @üye` — Üyenin uyarı geçmişini listeler\n"
            "`/uyarisil @üye` — Üyenin tüm uyarılarını temizler\n"
            "`/temizle <sayı>` — Kanalda belirtilen miktarda mesaj siler"
        ),
    },
    "kanal": {
        "emoji": "📌",
        "title": "Kanal Yönetimi",
        "description": (
            "`/kilitle` — Kanalı mesaj gönderimine kapatır\n"
            "`/kilitac` — Kanalı mesaj gönderimine açar\n"
            "`/yavaslat <saniye>` — Kanal yavaş modunu (slowmode) ayarlar"
        ),
    },
    "ses": {
        "emoji": "🔊",
        "title": "Ses Kanalı",
        "description": (
            "`/sesegir [kanal]` — Belirtilen ses kanalına girer ve sürekli kalır\n"
            "`/sestenayril` — Bağlı olunan ses kanalından ayrılır\n"
            "`/sesdurum` — Botun ses kanalı durumunu gösterir"
        ),
    },
    "seviye": {
        "emoji": "📈",
        "title": "Seviye",
        "description": (
            "`/seviye` — Seviye sistemi yönetim panelini açar\n"
            "`/seviye-set @üye <seviye>` — Üyenin seviyesini doğrudan ayarlar\n"
            "`/rank [@üye]` — Seviye kartınızı görüntüler"
        ),
    },
    "karşılama": {
        "emoji": "👋",
        "title": "Karşılama",
        "description": (
            "`/karşılama` — Karşılama (giriş-çıkış) sistemi yönetim panelini açar\n"
            "`/hoşgeldin-kurulum #kanal [mesaj]` — Giriş mesajı şablonu ve kanalını ayarlar"
        ),
    },
    "kullanıcı": {
        "emoji": "👤",
        "title": "Kullanıcı",
        "description": (
            "`/rank` — Seviye kartınızı görüntüler\n"
            "`/kb` — Kullanıcı hakkında bilgi verir\n"
            "`/avatar` — Profil fotoğrafını gösterir"
        ),
    },
    "kelime_filtresi": {
        "emoji": "🚫",
        "title": "Kelime Filtresi",
        "description": (
            "`c!kelimeekle <kelime>` — Yasaklı kelime listesine kelime ekler\n"
            "`c!kelimesil <kelime>` — Yasaklı kelime listesinden kelime çıkarır\n"
            "`c!kelimeler` — Sunucudaki tüm yasaklı kelimeleri listeler\n"
            "`c!kelimetemizle` — Tüm yasaklı kelimeleri sıfırlar (Admin)"
        ),
    },
}

def create_help_embed(bot, key):
    cat = CATEGORIES[key]
    embed = discord.Embed(
        title=f"{cat['emoji']} {cat['title']}",
        description=cat["description"],
        color=COLOR,
    )
    if bot.user and bot.user.display_avatar:
        embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    total_cmds = len(bot.commands)
    embed.set_footer(text=f"Sistemde toplam {total_cmds} komut yüklü • Menüden kategori seçebilirsiniz.")
    return embed

class YardimSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label=cat["title"],
                value=key,
                emoji=cat["emoji"],
                description=f"{cat['title']} komutlarını göster",
            )
            for key, cat in CATEGORIES.items()
            if key != "ana_sayfa"
        ]
        options.insert(
            0,
            discord.SelectOption(label="Ana Sayfa", value="ana_sayfa", emoji="🏠", description="Ana menüye dön"),
        )
        super().__init__(placeholder="📂 Bir kategori seç...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        embed = create_help_embed(self.bot, selection)
        await interaction.response.edit_message(embed=embed, view=self.view)

class YardimView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.add_item(YardimSelect(bot))
        self.message = None

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="yardım", description="Botun interaktif yardım menüsünü açar.")
    async def help(self, ctx):
        """Kullanıcılara botun tüm komutlarını ve kullanım yönergelerini interaktif bir arayüzle sunar."""
        view = YardimView(self.bot)
        embed = create_help_embed(self.bot, "ana_sayfa")
        embed.description = (
            "Aşağıdaki açılır menüden bir kategori seçerek komutları listeleyebilirsiniz. 👇\n\n"
            f"🛡️ **Güvenlik** • 🔨 **Moderasyon** • 📌 **Kanal Yönetimi**\n"
            f"🔊 **Ses Kanalı** • 📈 **Seviye** • 👋 **Karşılama**\n"
            f"👤 **Kullanıcı** • 🚫 **Kelime Filtresi**"
        )
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

async def setup(bot):
    await bot.add_cog(Help(bot))

# Yusuf Cebeci @58tc
