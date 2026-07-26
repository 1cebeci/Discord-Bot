import discord
from discord.ext import commands
import json
import asyncio
import random
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.resolve() / "data"
LVL_CONF = DATA_DIR / "levels_config.json"
LVL_DATA = DATA_DIR / "levels.json"

def default_conf():
    return {"aktif": False, "kanal": None, "roller": {}}

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self._load_data(LVL_DATA)
        self.conf = self._load_data(LVL_CONF)
        self.cooldowns = {}

    def _load_data(self, path):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _save_conf(self):
        def _write():
            LVL_CONF.parent.mkdir(parents=True, exist_ok=True)
            LVL_CONF.write_text(json.dumps(self.conf, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    async def _save_data(self):
        def _write():
            LVL_DATA.parent.mkdir(parents=True, exist_ok=True)
            LVL_DATA.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    @commands.hybrid_command(name="seviye", description="Seviye sistemi yönetim panelini açar.")
    @commands.has_permissions(administrator=True)
    async def lvl_panel(self, ctx):
        """Seviye sistemi ayarlarını kontrol panelinden yönetmenizi sağlar."""
        settings_cog = self.bot.get_cog("Settings")
        if settings_cog:
            try:
                from cogs.settings import ControlPanelView
            except ImportError:
                from settings import ControlPanelView
            
            embed = await settings_cog.create_panel_embed(ctx.guild.id, "leveling")
            view = ControlPanelView(self.bot, settings_cog, ctx.guild.id, ctx.author.id, initial_tab="leveling")
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("❌ Ayarlar sistemi (Settings cog) yüklenemedi.")

    @commands.hybrid_command(name="seviye-set", aliases=["levelset", "setlevel"], description="Bir üyenin seviyesini doğrudan ayarlar.")
    @commands.has_permissions(administrator=True)
    async def set_level(self, ctx, member: discord.Member, level: int):
        """Belirtilen üyenin seviye ve tecrübe puanı (XP) değerini günceller."""
        if level < 1:
            return await ctx.send("❌ Seviye 1'den küçük olamaz.")
        gid = str(ctx.guild.id)
        uid = str(member.id)
        self.data.setdefault(gid, {})
        self.data[gid].setdefault(uid, {"xp": 0, "lvl": 1})
        self.data[gid][uid]["lvl"] = level
        self.data[gid][uid]["xp"] = (level - 1) * 300
        await self._save_data()
        await self.assign_level_roles(member, gid, level)
        await ctx.send(f"✅ {member.mention} üyesinin seviyesi **{level}** olarak ayarlandı.")

    async def assign_level_roles(self, member: discord.Member, guild_id: str, lvl: int):
        conf = self.conf.get(guild_id, default_conf())
        roller = conf.get("roller", {})
        if not roller:
            return
        verilecekler = [rid for l, rid in roller.items() if int(l) <= lvl]
        for rid in verilecekler:
            rol = member.guild.get_role(int(rid))
            if rol and rol not in member.roles:
                try:
                    await member.add_roles(rol, reason=f"Seviye {lvl} ödülü")
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        gid = str(message.guild.id)
        conf = self.conf.get(gid)
        if not conf or not conf.get("aktif"):
            return

        uid = str(message.author.id)
        
        now = datetime.utcnow().timestamp()
        key = (gid, uid)
        last_xp = self.cooldowns.get(key, 0)
        if now - last_xp < 60:
            return
        self.cooldowns[key] = now

        self.data.setdefault(gid, {})
        self.data[gid].setdefault(uid, {"xp": 0, "lvl": 1})

        self.data[gid][uid]["xp"] += random.randint(5, 15)
        gerekli_xp = self.data[gid][uid]["lvl"] * 300

        if self.data[gid][uid]["xp"] >= gerekli_xp:
            self.data[gid][uid]["lvl"] += 1
            yeni_lvl = self.data[gid][uid]["lvl"]
            await self._save_data()

            await self.assign_level_roles(message.author, gid, yeni_lvl)

            kanal_id = conf.get("kanal")
            if kanal_id:
                kanal = message.guild.get_channel(int(kanal_id))
                if kanal:
                    try:
                        await kanal.send(f"🎊 {message.author.mention} **Seviye {yeni_lvl}** oldu!")
                    except discord.Forbidden:
                        pass
        else:
            await self._save_data()

    @commands.hybrid_command(name="rank", description="Mevcut seviye kartınızı gösterir.")
    async def rank(self, ctx, member: discord.Member = None):
        """Kullanıcının seviyesini, toplam tecrübe puanını (XP) ve seviye ilerleme çubuğunu görüntüler."""
        m = member or ctx.author
        u = self.data.get(str(ctx.guild.id), {}).get(str(m.id), {"xp": 0, "lvl": 1})
        gerekli = u["lvl"] * 300
        oran = min(u["xp"] / gerekli, 1.0)
        dolu = int(oran * 10)
        bar = "🟩" * dolu + "⬜" * (10 - dolu)
        embed = discord.Embed(title=f"📈 {m.display_name}", color=discord.Color.blurple())
        embed.add_field(name="Seviye", value=str(u["lvl"]), inline=True)
        embed.add_field(name="XP", value=f"{u['xp']} / {gerekli}", inline=True)
        embed.add_field(name="İlerleme", value=bar, inline=False)
        embed.set_thumbnail(url=m.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))

# Yusuf Cebeci @58tc
