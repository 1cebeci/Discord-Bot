import discord
from discord.ext import commands
import json
import asyncio
from pathlib import Path

DATA_DIR = Path(__file__).parent.resolve() / "data"
W_FILE = DATA_DIR / "welcome_config.json"

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self._load()

    def _load(self):
        if W_FILE.exists():
            try:
                return json.loads(W_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _save(self):
        def _write():
            W_FILE.parent.mkdir(exist_ok=True, parents=True)
            W_FILE.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    def _guild_config(self, guild_id):
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {
                "w_aktif": False,
                "l_aktif": False,
                "w_channel": None,
                "w_msg": "Hoş geldin {üye}! Seninle birlikte {sayı} kişiyiz.",
                "l_msg": "Görüşürüz {üye}! Sunucumuz {sayı} kişi kaldı."
            }
        return self.config[gid]

    @commands.hybrid_command(name="karşılama", description="Giriş-çıkış (karşılama) sistemi yönetim panelini açar.")
    @commands.has_permissions(administrator=True)
    async def welcome_panel(self, ctx):
        """Giriş-çıkış mesaj sistemini kontrol panelinden yönetmenizi sağlar."""
        settings_cog = self.bot.get_cog("Settings")
        if settings_cog:
            try:
                from cogs.settings import ControlPanelView
            except ImportError:
                from settings import ControlPanelView
            
            embed = await settings_cog.create_panel_embed(ctx.guild.id, "welcome")
            view = ControlPanelView(self.bot, settings_cog, ctx.guild.id, ctx.author.id, initial_tab="welcome")
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("❌ Ayarlar sistemi (Settings cog) yüklenemedi.")

    @commands.hybrid_command(name="hoşgeldin-kurulum", description="Giriş mesajını ve kanalını doğrudan ayarlar.")
    @commands.has_permissions(administrator=True)
    async def w_setup(self, ctx, kanal: discord.TextChannel, *, mesaj: str):
        """Kanalı belirler, mesaj şablonunu ayarlar ve karşılama sistemini otomatik olarak aktif hale getirir."""
        gid = str(ctx.guild.id)
        cfg = self._guild_config(gid)
        cfg.update({
            "w_channel": str(kanal.id),
            "w_msg": mesaj,
            "w_aktif": True
        })
        await self._save()
        await ctx.send(f"✅ Hoş geldin kanalı {kanal.mention} olarak ayarlandı ve sistem açıldı.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        c = self.config.get(str(member.guild.id))
        if c and c.get("w_aktif") and c.get("w_channel"):
            chan = member.guild.get_channel(int(c["w_channel"]))
            if chan:
                msg = c.get("w_msg", "Hoş geldin {üye}").replace("{üye}", member.mention).replace("{sayı}", str(member.guild.member_count))
                try:
                    await chan.send(msg)
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        c = self.config.get(str(member.guild.id))
        if c and c.get("l_aktif") and c.get("w_channel"):
            chan = member.guild.get_channel(int(c["w_channel"]))
            if chan:
                msg = c.get("l_msg", "Görüşürüz {üye}").replace("{üye}", member.name).replace("{sayı}", str(member.guild.member_count))
                try:
                    await chan.send(msg)
                except discord.Forbidden:
                    pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))

# Yusuf Cebeci @58tc
