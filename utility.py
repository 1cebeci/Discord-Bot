import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Botun gecikme süresini ölçer.")
    async def ping(self, ctx):
        """Botun Discord API'sine olan gecikmesini milisaniye cinsinden gösterir."""
        await ctx.send(f"🏓 Pong! Gecikme: {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_command(name="avatar", aliases=["pp"], description="Bir kullanıcının profil fotoğrafını gösterir.")
    async def avatar(self, ctx, member: discord.Member = None):
        """Belirtilen üyenin (veya kendinizin) profil resmini büyük boyutta gösterir."""
        if member is None and ctx.message and ctx.message.reference:
            try:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                member = msg.author
            except Exception:
                pass
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.name} Avatarı", color=discord.Color.blue())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kb", aliases=["kullanıcı-bilgi", "whois"], description="Kullanıcı hakkında bilgi verir.")
    async def kb(self, ctx, member: discord.Member = None):
        """Kullanıcının hesabı ve sunucudaki durumu hakkında temel bilgileri gösterir."""
        member = member or ctx.author
        embed = discord.Embed(title=f"👤 Kullanıcı: {member.name}", color=0x2f3136)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Katılım Tarihi", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sb", aliases=["sunucu-bilgi"], description="Sunucu hakkında bilgi verir.")
    async def sb(self, ctx):
        """Mevcut Discord sunucusunun üye sayısı, ID'si ve temel verilerini listeler."""
        g = ctx.guild
        embed = discord.Embed(title=f"🏰 {g.name} Bilgileri", color=discord.Color.green())
        embed.add_field(name="Üye Sayısı", value=g.member_count, inline=True)
        embed.add_field(name="Sunucu ID", value=g.id, inline=True)
        if g.icon: 
            embed.set_thumbnail(url=g.icon.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))

# Yusuf Cebeci @58tc
