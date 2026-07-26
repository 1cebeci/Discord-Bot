import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="espiri", aliases=["espri"], description="Rastgele komik bir espri gönderir.")
    async def espiri(self, ctx):
        """Eğlenceli ve soğuk esprilerden birini kanala gönderir."""
        espriler = [
            "Dün bir araba çizdim, benzinle boyamak istedim.",
            "Sinemada on dakika ara dediler, gittim aradım bulamadım.",
            "Geçen gün bir taksi çevirdim hala dönüyor.",
            "Röntgen filmi çektirdik, yakında sinemalarda."
        ]
        await ctx.send(f"🤣 {random.choice(espriler)}")

    @commands.hybrid_command(name="yazıtura", description="Yazı tura atar.")
    async def yazitura(self, ctx):
        """Madeni para atışı yaparak sonucu (Yazı veya Tura) söyler."""
        await ctx.send(f"🪙 Sonuç: **{random.choice(['Yazı', 'Tura'])}**")

async def setup(bot):
    await bot.add_cog(Fun(bot))

# Yusuf Cebeci @58tc
