import discord
from discord.ext import commands
import json
import re
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.resolve() / "data"
SEC_FILE = DATA_DIR / "security_settings.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "link": True,
    "kufur": True,
    "reklam": True,
    "spam": True,
    "caps": True,
    "whitelist": []
}

SWEAR_WORDS = ["amk", "oç", "piç", "sik", "ananı", "yarrak"]
LINK_PATTERN = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
INVITE_PATTERN = re.compile(r"(discord\.gg/\S+|discord(app)?\.com/invite/\S+)", re.IGNORECASE)

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ayarlar = self._load()
        self.message_history = {}

    def _load(self):
        if SEC_FILE.exists():
            try:
                return json.loads(SEC_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _kaydet(self):
        def _write():
            SEC_FILE.parent.mkdir(exist_ok=True, parents=True)
            SEC_FILE.write_text(json.dumps(self.ayarlar, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    def _guild_ayar(self, guild_id):
        gid = str(guild_id)
        if gid not in self.ayarlar:
            self.ayarlar[gid] = DEFAULT_SETTINGS.copy()
            self.ayarlar[gid]["whitelist"] = []
            try:
                SEC_FILE.parent.mkdir(exist_ok=True, parents=True)
                SEC_FILE.write_text(json.dumps(self.ayarlar, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
        else:
            changed = False
            for k, v in DEFAULT_SETTINGS.items():
                if k not in self.ayarlar[gid]:
                    self.ayarlar[gid][k] = v
                    changed = True
            if changed:
                try:
                    SEC_FILE.write_text(json.dumps(self.ayarlar, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
        return self.ayarlar[gid]

    async def _log_gonder(self, guild, embed):
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return
            log_id = data.get(str(guild.id), {}).get("log_kanal")
            if log_id:
                kanal = guild.get_channel(int(log_id))
                if kanal:
                    try:
                        await kanal.send(embed=embed)
                    except discord.Forbidden:
                        pass

    def _yetkili_muaf_mi(self, message):
        perms = message.author.guild_permissions
        return perms.administrator or perms.manage_messages

    def _whitelist_mi(self, content, whitelist):
        return any(domain.lower() in content for domain in whitelist)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if self._yetkili_muaf_mi(message):
            return

        data = self._guild_ayar(message.guild.id)
        content = message.content

        if data.get("spam", True):
            now = datetime.utcnow().timestamp()
            key = (message.guild.id, message.author.id)
            self.message_history.setdefault(key, [])
            self.message_history[key] = [t for t in self.message_history[key] if now - t < 4]
            self.message_history[key].append(now)

            if len(self.message_history[key]) >= 5:
                self.message_history[key] = []
                try:
                    await message.delete()
                except Exception:
                    pass
                try:
                    await message.author.timeout(timedelta(minutes=10), reason="Spam koruması tetiklendi.")
                    await message.channel.send(f"⚠️ {message.author.mention}, çok hızlı mesaj gönderdiğin için 10 dakika susturuldun!", delete_after=5)
                except discord.Forbidden:
                    await message.channel.send(f"⚠️ {message.author.mention}, lütfen spam yapma!", delete_after=5)
                await self._logla(message, "Spam Filtresi", "4 saniyede 5+ mesaj gönderimi")
                return

        if data.get("caps", True) and len(content) > 5:
            upper_count = sum(1 for c in content if c.isupper())
            letter_count = sum(1 for c in content if c.isalpha())
            if letter_count > 0 and (upper_count / letter_count) > 0.7:
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen aşırı büyük harf kullanma!", delete_after=4)
                await self._logla(message, "Büyük Harf Filtresi", f"Mesajın %{int((upper_count/letter_count)*100)}'si büyük harf")
                return

        content_lower = content.lower()

        if data.get("kufur", True):
            for word in SWEAR_WORDS:
                if re.search(rf"\b{re.escape(word)}\b", content_lower):
                    await self._sil_ve_uyar(message, f"⚠️ {message.author.mention}, lütfen kelimelerine dikkat et!")
                    await self._logla(message, "Küfür Filtresi", word)
                    return

        if data.get("reklam", True) and INVITE_PATTERN.search(content_lower):
            await self._sil_ve_uyar(message, f"📢 {message.author.mention}, sunucu reklamı yapmak yasak!")
            await self._logla(message, "Reklam Filtresi", "Davet linki")
            return

        if data.get("link", True) and LINK_PATTERN.search(content_lower):
            if not self._whitelist_mi(content_lower, data.get("whitelist", [])):
                await self._sil_ve_uyar(message, f"🚫 {message.author.mention}, link paylaşımı yasak!")
                await self._logla(message, "Link Filtresi", "Beyaz listede olmayan link")
                return

    async def _sil_ve_uyar(self, message, warning_msg):
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass
        try:
            await message.channel.send(warning_msg, delete_after=4)
        except discord.Forbidden:
            pass

    async def _logla(self, message, filter_type, detail):
        embed = discord.Embed(
            title="🛡️ Güvenlik Müdahalesi",
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="Üye", value=message.author.mention, inline=True)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
        embed.add_field(name="Filtre", value=filter_type, inline=True)
        embed.add_field(name="Ayrıntı", value=detail, inline=False)
        await self._log_gonder(message.guild, embed)

    @commands.hybrid_command(name="güvenlik", aliases=["security"], description="Güvenlik filtreleri kontrol panelini açar.")
    @commands.has_permissions(administrator=True)
    async def guvenlik(self, ctx):
        """Güvenlik yönetim panelini doğrudan açar."""
        settings_cog = self.bot.get_cog("Settings")
        if settings_cog:
            try:
                from cogs.settings import ControlPanelView
            except ImportError:
                from settings import ControlPanelView
            
            embed = await settings_cog.create_panel_embed(ctx.guild.id, "security")
            view = ControlPanelView(self.bot, settings_cog, ctx.guild.id, ctx.author.id, initial_tab="security")
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("❌ Ayarlar sistemi (Settings cog) yüklenemedi.")

    @commands.hybrid_command(name="izinliekle", aliases=["whitelist_add"], description="Domaini güvenli link listesine ekler.")
    @commands.has_permissions(administrator=True)
    async def whitelist_add(self, ctx, domain: str):
        """Belirtilen domaini link engelleyici filtresinin beyaz listesine ekler."""
        gid = str(ctx.guild.id)
        data = self._guild_ayar(gid)
        domain = domain.lower().strip()
        if domain in data["whitelist"]:
            return await ctx.send(f"⚠️ `{domain}` zaten izinli listede.")
        data["whitelist"].append(domain)
        await self._kaydet()
        await ctx.send(f"✅ `{domain}` artık link filtresinden muaf.")

    @commands.hybrid_command(name="izinlisil", aliases=["whitelist_remove"], description="Domaini güvenli link listesinden çıkarır.")
    @commands.has_permissions(administrator=True)
    async def whitelist_remove(self, ctx, domain: str):
        """Belirtilen domaini link engelleyici filtresinin beyaz listesinden kaldırır."""
        gid = str(ctx.guild.id)
        data = self._guild_ayar(gid)
        domain = domain.lower().strip()
        if domain not in data["whitelist"]:
            return await ctx.send(f"❌ `{domain}` izinli listede bulunmuyor.")
        data["whitelist"].remove(domain)
        await self._kaydet()
        await ctx.send(f"🧹 `{domain}` izinli listeden çıkarıldı.")

    @commands.hybrid_command(name="logkanali", aliases=["setlogchannel"], description="Güvenlik log kanalını ayarlar.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, kanal: discord.TextChannel):
        """Güvenlik filtrelerinin log bildirimlerinin gönderileceği kanalı belirler."""
        SETTINGS_FILE.parent.mkdir(exist_ok=True, parents=True)
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8")) if SETTINGS_FILE.exists() else {}
        except Exception:
            data = {}
        data.setdefault(str(ctx.guild.id), {})["log_kanal"] = kanal.id
        
        def _write():
            SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)
        await ctx.send(f"✅ Güvenlik log kanalı {kanal.mention} olarak ayarlandı.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command is None or ctx.cog is not self:
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bu komutu kullanmak için yönetici yetkisine sahip olman gerekiyor.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Belirtilen kanal bulunamadı.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik parametre: `{error.param.name}`.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Security(bot))

# Yusuf Cebeci @58tc
