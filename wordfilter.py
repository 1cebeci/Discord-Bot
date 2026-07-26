import discord
from discord.ext import commands
import json
import re
import asyncio
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.resolve() / "data"
WF_FILE = DATA_DIR / "wordfilter.json"
SETTINGS_FILE = DATA_DIR / "settings.json"


class WordFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self._load()

    def _load(self):
        if WF_FILE.exists():
            try:
                return json.loads(WF_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _kaydet(self):
        def _write():
            WF_FILE.parent.mkdir(exist_ok=True, parents=True)
            WF_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    def _guild_kelimeler(self, guild_id: str) -> list:
        return self.data.setdefault(str(guild_id), [])

    def _yetkili_mi(self, message):
        perms = message.author.guild_permissions
        return perms.administrator or perms.manage_messages

    async def _log_gonder(self, guild, embed):
        if SETTINGS_FILE.exists():
            try:
                settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return
            log_id = settings.get(str(guild.id), {}).get("log_kanal")
            if log_id:
                kanal = guild.get_channel(int(log_id))
                if kanal:
                    try:
                        await kanal.send(embed=embed)
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if self._yetkili_mi(message):
            return

        gid = str(message.guild.id)
        kelimeler = self._guild_kelimeler(gid)
        if not kelimeler:
            return

        content_lower = message.content.lower()

        for kelime in kelimeler:
            pattern = re.compile(rf"\b{re.escape(kelime.lower())}\b", re.IGNORECASE)
            if pattern.search(content_lower):
                try:
                    await message.delete()
                except (discord.Forbidden, discord.NotFound):
                    pass
                try:
                    await message.channel.send(
                        f"Yasak kelime kullandin, mesajin silindi! {message.author.mention}",
                        delete_after=5
                    )
                except discord.Forbidden:
                    pass

                embed = discord.Embed(
                    title="Kelime Filtresi Tetiklendi",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Uye", value=message.author.mention, inline=True)
                embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
                embed.add_field(name="Tespit Edilen Kelime", value=f"`{kelime}`", inline=True)
                embed.set_footer(text=f"Sunucu: {message.guild.name}")
                await self._log_gonder(message.guild, embed)
                return

    @commands.hybrid_command(name="kelimeekle", aliases=["wordadd"], description="Yasakli kelime listesine kelime ekler.")
    @commands.has_permissions(manage_messages=True)
    async def kelime_ekle(self, ctx, *, kelime: str):
        """Sunucuya ozel yasakli kelime listesine yeni kelime ekler."""
        gid = str(ctx.guild.id)
        kelime = kelime.lower().strip()
        kelimeler = self._guild_kelimeler(gid)

        if kelime in kelimeler:
            return await ctx.send(f"Bu kelime zaten yasakli listesinde: `{kelime}`")

        kelimeler.append(kelime)
        await self._kaydet()

        embed = discord.Embed(
            title="Kelime Eklendi",
            description=f"`{kelime}` yasakli kelime listesine eklendi.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Toplam yasakli kelime: {len(kelimeler)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kelimesil", aliases=["wordremove"], description="Yasakli kelime listesinden kelime cikarir.")
    @commands.has_permissions(manage_messages=True)
    async def kelime_sil(self, ctx, *, kelime: str):
        """Sunucuya ozel yasakli kelime listesinden belirtilen kelimeyi kaldirir."""
        gid = str(ctx.guild.id)
        kelime = kelime.lower().strip()
        kelimeler = self._guild_kelimeler(gid)

        if kelime not in kelimeler:
            return await ctx.send(f"Bu kelime yasakli listesinde bulunamadi: `{kelime}`")

        kelimeler.remove(kelime)
        await self._kaydet()

        embed = discord.Embed(
            title="Kelime Silindi",
            description=f"`{kelime}` yasakli kelime listesinden cikarildi.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Kalan yasakli kelime: {len(kelimeler)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kelimeler", aliases=["wordlist"], description="Sunucudaki yasakli kelime listesini gosterir.")
    @commands.has_permissions(manage_messages=True)
    async def kelime_listesi(self, ctx):
        """Sunucuya ozel yasakli kelime listesini gosterir."""
        gid = str(ctx.guild.id)
        kelimeler = self._guild_kelimeler(gid)

        embed = discord.Embed(
            title="Yasakli Kelime Listesi",
            color=discord.Color.red()
        )

        if not kelimeler:
            embed.description = "*Henuz yasakli kelime eklenmemis.*"
            embed.color = discord.Color.green()
        else:
            embed.description = "\n".join(f"`{k}`" for k in kelimeler)
            embed.set_footer(text=f"Toplam: {len(kelimeler)} kelime")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kelimetemizle", aliases=["wordclear"], description="Tum yasakli kelimeleri siler.")
    @commands.has_permissions(administrator=True)
    async def kelime_temizle(self, ctx):
        """Sunucuya ozel tum yasakli kelimeleri sifirlar."""
        gid = str(ctx.guild.id)
        self.data[gid] = []
        await self._kaydet()
        await ctx.send("Tum yasakli kelimeler temizlendi.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command is None or ctx.cog is not self:
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Bu komutu kullanmak icin Mesajlari Yonet yetkisine ihtiyacin var.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Eksik parametre: `{error.param.name}`. Ornek: `c!kelimeekle kufur`")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(WordFilter(bot))

# Yusuf Cebeci @58tc
