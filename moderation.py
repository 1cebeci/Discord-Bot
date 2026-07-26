import discord
from discord.ext import commands
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.resolve() / "data"
WARN_FILE = DATA_DIR / "warnings.json"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.warns = json.loads(WARN_FILE.read_text(encoding="utf-8")) if WARN_FILE.exists() else {}
        except Exception:
            self.warns = {}

    async def _kaydet_warns(self):
        def _write():
            WARN_FILE.parent.mkdir(exist_ok=True, parents=True)
            WARN_FILE.write_text(json.dumps(self.warns, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    async def send_log(self, guild, embed):
        dosya = DATA_DIR / "settings.json"
        if dosya.exists():
            try:
                data = json.loads(dosya.read_text(encoding="utf-8"))
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

    def _hiyerarsi_kontrol(self, ctx, hedef):
        if hedef.id == ctx.guild.owner_id:
            return "❌ Sunucu sahibine bu işlem uygulanamaz."
        if hedef == ctx.author:
            return "❌ Bu işlemi kendine uygulayamazsın."
        if hedef.id == self.bot.user.id:
            return "❌ Bana bu işlemi uygulayamazsın."
        if ctx.author.id != ctx.guild.owner_id and hedef.top_role >= ctx.author.top_role:
            return "❌ Bu üye senden eşit veya daha üst rolde, işlem yapamazsın."
        if hedef.top_role >= ctx.guild.me.top_role:
            return "❌ Bu üye benden üst rolde, işlemi gerçekleştiremiyorum."
        return None

    def _base_embed(self, title, color, ctx, hedef=None, sebep=None):
        embed = discord.Embed(title=title, color=color, timestamp=datetime.utcnow())
        if hedef:
            embed.add_field(name="Üye", value=f"{hedef.mention} (`{hedef.id}`)", inline=True)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
        if sebep:
            embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_footer(text=f"Sunucu: {ctx.guild.name}")
        return embed


    @commands.hybrid_command(name="ban", description="Belirtilen üyeyi sunucudan yasaklar.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, sebep: str = "Belirtilmedi"):
        """Üyeyi kalıcı olarak sunucudan yasaklar ve DM üzerinden bilgilendirmeye çalışır."""
        hata = self._hiyerarsi_kontrol(ctx, member)
        if hata:
            return await ctx.send(hata)

        try:
            await member.send(
                embed=discord.Embed(
                    title="🚫 Yasaklandın",
                    description=f"**{ctx.guild.name}** sunucusundan yasaklandın.\n**Sebep:** {sebep}",
                    color=discord.Color.red(),
                )
            )
        except discord.Forbidden:
            pass

        await member.ban(reason=f"{ctx.author} tarafından: {sebep}")
        embed = self._base_embed("🚫 Üye Yasaklandı", discord.Color.red(), ctx, member, sebep)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)

    @commands.hybrid_command(name="unban", description="Belirtilen kullanıcının yasağını kaldırır.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, kullanici: str):
        """Kullanıcının yasaklılar listesinden kaydını siler (ID veya isim#tag girilmelidir)."""
        banlar = [entry async for entry in ctx.guild.bans()]

        hedef = None
        if kullanici.isdigit():
            hedef = discord.utils.find(lambda b: b.user.id == int(kullanici), banlar)
        else:
            hedef = discord.utils.find(
                lambda b: str(b.user) == kullanici or b.user.name == kullanici, banlar
            )

        if not hedef:
            return await ctx.send("❌ Bu kullanıcı ban listesinde bulunamadı. ID veya `kullanıcı#0000` formatını dene.")

        await ctx.guild.unban(hedef.user, reason=f"{ctx.author} tarafından unban")
        embed = discord.Embed(
            title="✅ Yasak Kaldırıldı",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="Üye", value=f"{hedef.user} (`{hedef.user.id}`)", inline=True)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Sunucu: {ctx.guild.name}")
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)


    @commands.hybrid_command(name="kick", aliases=["at"], description="Belirtilen üyeyi sunucudan atar.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, sebep: str = "Belirtilmedi"):
        """Üyenin sunucuyla ilişiğini keser (atılmasını sağlar)."""
        hata = self._hiyerarsi_kontrol(ctx, member)
        if hata:
            return await ctx.send(hata)

        await member.kick(reason=f"{ctx.author} tarafından: {sebep}")
        embed = self._base_embed("👢 Üye Sunucudan Atıldı", discord.Color.orange(), ctx, member, sebep)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)


    @commands.hybrid_command(name="mute", aliases=["sustur"], description="Üyeyi belirli bir süre susturur.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, sure: str = "10m", *, sebep: str = "Belirtilmedi"):
        """Üyeye zaman aşımı (timeout) uygular. Süre formatı: 10s (saniye), 10m (dakika), 2h (saat), 1d (gün)."""
        hata = self._hiyerarsi_kontrol(ctx, member)
        if hata:
            return await ctx.send(hata)

        birim_map = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
        try:
            birim = sure[-1]
            miktar = int(sure[:-1])
            if birim not in birim_map:
                raise ValueError
            delta = timedelta(**{birim_map[birim]: miktar})
        except (ValueError, IndexError):
            return await ctx.send("❌ Geçersiz süre formatı. Örnek: `10m`, `1h`, `1d`")

        if delta.total_seconds() > 28 * 24 * 3600:
            return await ctx.send("❌ Discord kuralları gereği en fazla 28 günlük susturma uygulanabilir.")

        await member.timeout(delta, reason=f"{ctx.author} tarafından: {sebep}")
        embed = self._base_embed("🔇 Üye Susturuldu", discord.Color.dark_grey(), ctx, member, sebep)
        embed.add_field(name="Süre", value=sure, inline=True)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)

    @commands.hybrid_command(name="unmute", aliases=["susturmakaldir"], description="Susturulmuş üyenin susturmasını kaldırır.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Üyenin zaman aşımını (timeout) kaldırarak konuşmasını sağlar."""
        if not member.is_timed_out():
            return await ctx.send("❌ Bu üye zaten susturulmuş durumda değil.")

        await member.timeout(None, reason=f"{ctx.author} tarafından susturma kaldırıldı")
        embed = self._base_embed("🔊 Susturma Kaldırıldı", discord.Color.green(), ctx, member)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)


    @commands.hybrid_command(name="uyar", aliases=["warn"], description="Belirtilen üyeye uyarı ekler.")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, sebep: str = "Belirtilmedi"):
        """Üyenin siciline uyarı ekler ve toplam uyarı sayısını gösterir."""
        hata = self._hiyerarsi_kontrol(ctx, member)
        if hata:
            return await ctx.send(hata)

        gid, uid = str(ctx.guild.id), str(member.id)
        self.warns.setdefault(gid, {}).setdefault(uid, [])
        self.warns[gid][uid].append(
            {"yetkili": str(ctx.author), "sebep": sebep, "tarih": datetime.utcnow().strftime("%d.%m.%Y %H:%M")}
        )
        await self._kaydet_warns()

        toplam = len(self.warns[gid][uid])
        embed = self._base_embed("⚠️ Üye Uyarıldı", discord.Color.gold(), ctx, member, sebep)
        embed.add_field(name="Toplam Uyarı", value=str(toplam), inline=True)
        await ctx.send(embed=embed)
        await self.send_log(ctx.guild, embed)

    @commands.hybrid_command(name="uyarılar", aliases=["warnings", "uyarilar"], description="Üyenin uyarı geçmişini listeler.")
    async def warnings_list(self, ctx, member: discord.Member = None):
        """Belirtilen üyenin (veya kendinizin) tüm uyarı kayıtlarını gösterir."""
        member = member or ctx.author
        gid, uid = str(ctx.guild.id), str(member.id)
        kayitlar = self.warns.get(gid, {}).get(uid, [])

        if not kayitlar:
            return await ctx.send(f"✅ {member.mention} adına kayıtlı uyarı bulunmuyor.")

        embed = discord.Embed(title=f"⚠️ {member.display_name} - Uyarı Geçmişi", color=discord.Color.gold())
        for i, w in enumerate(kayitlar, 1):
            embed.add_field(
                name=f"#{i} — {w['tarih']}",
                value=f"**Sebep:** {w['sebep']}\n**Yetkili:** {w['yetkili']}",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="uyarisil", aliases=["clearwarns"], description="Üyenin tüm uyarılarını siler.")
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Üyenin sicilindeki tüm uyarıları sıfırlar."""
        gid, uid = str(ctx.guild.id), str(member.id)
        if gid in self.warns and uid in self.warns[gid]:
            self.warns[gid][uid] = []
            await self._kaydet_warns()
        await ctx.send(f"🧹 {member.mention} adına kayıtlı tüm uyarılar silindi.")


    @commands.hybrid_command(name="temizle", aliases=["sil", "purge"], description="Kanalda belirtilen miktarda mesaj siler.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, miktar: int):
        """Kanalda 1 ile 100 arasında mesajı silerek sohbeti temizler."""
        if miktar < 1 or miktar > 100:
            return await ctx.send("❌ 1 ile 100 arasında bir değer girmelisin.")
        
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            silinen = await ctx.channel.purge(limit=miktar)
            await ctx.send(f"🗑️ {len(silinen)} mesaj temizlendi.")
        else:
            silinen = await ctx.channel.purge(limit=miktar + 1)
            await ctx.send(f"🗑️ {len(silinen) - 1} mesaj temizlendi.", delete_after=5)

    @commands.hybrid_command(name="kilitle", aliases=["lock"], description="Kanalı mesaj gönderimine kapatır.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx, kanal: discord.TextChannel = None):
        """Kanalın mesaj yazma iznini kaldırarak kilitler."""
        kanal = kanal or ctx.channel
        await kanal.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=discord.Embed(
            title="🔒 Kanal Kilitlendi",
            description=f"{kanal.mention} artık mesaj gönderimine kapalı.",
            color=discord.Color.red(),
        ))

    @commands.hybrid_command(name="kilitac", aliases=["unlock"], description="Kanalın kilidini açar.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx, kanal: discord.TextChannel = None):
        """Kanalın kilit durumunu kaldırarak tekrar yazılabilir hale getirir."""
        kanal = kanal or ctx.channel
        await kanal.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(embed=discord.Embed(
            title="🔓 Kanal Kilidi Açıldı",
            description=f"{kanal.mention} artık mesaj gönderimine açık.",
            color=discord.Color.green(),
        ))

    @commands.hybrid_command(name="yavaslat", aliases=["slowmode"], description="Kanalın yavaş mod süresini ayarlar.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, saniye: int):
        """Kanal yavaş modunu (slowmode) ayarlar. Devre dışı bırakmak için 0 yazılmalıdır."""
        if saniye < 0 or saniye > 21600:
            return await ctx.send("❌ 0 ile 21600 saniye arasında bir değer gir.")
        await ctx.channel.edit(slowmode_delay=saniye)
        if saniye == 0:
            await ctx.send("✅ Bu kanalda yavaş mod kapatıldı.")
        else:
            await ctx.send(f"🐢 Bu kanalda yavaş mod **{saniye} saniye** olarak ayarlandı.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command is None or ctx.cog is not self:
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bu komutu kullanmak için yeterli yetkin yok.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bu işlemi yapabilmem için sunucuda gerekli yetkilere sahip değilim.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Belirtilen üye bulunamadı.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik parametre: `{error.param.name}`. Komutu doğru kullandığından emin ol.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Geçersiz bir değer girdin, tekrar kontrol et.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Moderation(bot))

# Yusuf Cebeci @58tc
