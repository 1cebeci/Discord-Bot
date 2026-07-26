import discord
from discord.ext import commands, tasks
import asyncio
import time

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hedef_kanallar = {}
        self.son_deneme = {}
        self.kilitler = {}
        self.baglanti_kontrol.start()

    def cog_unload(self):
        self.baglanti_kontrol.cancel()

    def _kilit(self, guild_id):
        if guild_id not in self.kilitler:
            self.kilitler[guild_id] = asyncio.Lock()
        return self.kilitler[guild_id]

    @commands.hybrid_command(name="sesegir", aliases=["join"], description="Botu bir ses kanalına sokar.")
    @commands.has_permissions(administrator=True)
    async def sesegir(self, ctx, *, kanal: discord.VoiceChannel = None):
        """Botun belirtilen ses kanalına girmesini ve orada sürekli kalmasını sağlar."""
        if kanal is None:
            if ctx.author.voice and ctx.author.voice.channel:
                kanal = ctx.author.voice.channel
            else:
                return await ctx.send("❌ Bir ses kanalına gir ya da komuttan sonra kanal adı yaz: `/sesegir kanal: Genel`")

        perms = kanal.permissions_for(ctx.guild.me)
        if not perms.connect:
            return await ctx.send(f"❌ **{kanal.name}** kanalına girme iznim yok.")

        async with self._kilit(ctx.guild.id):
            try:
                vc = ctx.guild.voice_client
                if vc and vc.is_connected():
                    await vc.move_to(kanal)
                else:
                    if vc:
                        try:
                            await vc.disconnect(force=True)
                        except Exception:
                            pass
                    await kanal.connect(self_deaf=False, timeout=15, reconnect=False)
            except (asyncio.TimeoutError, discord.ClientException) as e:
                return await ctx.send(f"❌ Kanala bağlanamadım: `{e}`")

        self.hedef_kanallar[ctx.guild.id] = kanal.id
        self.son_deneme[ctx.guild.id] = time.time()
        await ctx.send(f"🔊 **{kanal.name}** kanalına girdim, çıkış komutu alana kadar burada kalacağım.")

    @commands.hybrid_command(name="sestenayril", aliases=["leave", "sestencik"], description="Botu ses kanalından çıkarır.")
    @commands.has_permissions(administrator=True)
    async def sestenayril(self, ctx):
        """Botun ses kanalından tamamen çıkmasını sağlar ve otomatik tekrar bağlanmayı durdurur."""
        self.hedef_kanallar.pop(ctx.guild.id, None)

        vc = ctx.guild.voice_client
        if vc and vc.is_connected():
            await vc.disconnect(force=True)
            await ctx.send("👋 Ses kanalından ayrıldım.")
        else:
            await ctx.send("❌ Zaten bir ses kanalında değilim.")

    @commands.hybrid_command(name="sesdurum", aliases=["voicestatus"], description="Botun ses durumunu gösterir.")
    async def sesdurum(self, ctx):
        """Botun şu anda herhangi bir ses kanalında olup olmadığını sorgular."""
        vc = ctx.guild.voice_client
        if vc and vc.is_connected():
            await ctx.send(f"🔊 Şu an **{vc.channel.name}** kanalındayım.")
        else:
            await ctx.send("🔇 Şu an hiçbir ses kanalında değilim.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        guild_id = member.guild.id
        if guild_id not in self.hedef_kanallar:
            return

        if after.channel is not None:
            return

        await self._guvenli_yeniden_baglan(member.guild)

    @tasks.loop(seconds=60)
    async def baglanti_kontrol(self):
        for guild_id in list(self.hedef_kanallar.keys()):
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            son = self.son_deneme.get(guild_id, 0)
            if time.time() - son < 20:
                continue

            vc = guild.voice_client
            if not vc or not vc.is_connected():
                await self._guvenli_yeniden_baglan(guild)

    @baglanti_kontrol.before_loop
    async def once_ready(self):
        await self.bot.wait_until_ready()

    async def _guvenli_yeniden_baglan(self, guild):
        kanal_id = self.hedef_kanallar.get(guild.id)
        if not kanal_id:
            return

        async with self._kilit(guild.id):
            vc = guild.voice_client
            if vc and vc.is_connected():
                return

            son = self.son_deneme.get(guild.id, 0)
            if time.time() - son < 10:
                return
            self.son_deneme[guild.id] = time.time()

            kanal = guild.get_channel(kanal_id)
            if not kanal:
                self.hedef_kanallar.pop(guild.id, None)
                return

            try:
                if vc:
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass
                await kanal.connect(self_deaf=True, timeout=15, reconnect=False)
            except (asyncio.TimeoutError, discord.ClientException):
                pass

async def setup(bot):
    await bot.add_cog(Voice(bot))

# Yusuf Cebeci @58tc
