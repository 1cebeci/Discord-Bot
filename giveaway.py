import discord
from discord.ext import commands, tasks
import json
import asyncio
import random
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.resolve() / "data"
G_FILE = DATA_DIR / "giveaways.json"

class GiveawayView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Katıl 🎉", custom_id="giveaway_join_button", style=discord.ButtonStyle.blurple)
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        mid = str(interaction.message.id)
        if mid not in self.cog.giveaways:
            return await interaction.response.send_message("❌ Bu çekiliş bulunamadı veya sona ermiş.", ephemeral=True)

        g_data = self.cog.giveaways[mid]
        if g_data.get("ended", False):
            return await interaction.response.send_message("❌ Bu çekiliş zaten sona ermiş.", ephemeral=True)

        uid = interaction.user.id
        joined = False

        if uid in g_data["participants"]:
            g_data["participants"].remove(uid)
            await self.cog._save()
        else:
            g_data["participants"].append(uid)
            await self.cog._save()
            joined = True

        embed = interaction.message.embeds[0]
        embed.description = f"Ödül: **{g_data['prize']}**\nSona Erme: <t:{int(g_data['end_time'])}:R>\nKatılımcı Sayısı: **{len(g_data['participants'])}**"
        button.label = f"Katıl ({len(g_data['participants'])}) 🎉"
        await interaction.response.edit_message(embed=embed, view=self)

        if joined:
            await interaction.followup.send("🎉 Çekilişe başarıyla katıldın!", ephemeral=True)
        else:
            await interaction.followup.send("👋 Çekiliş katılımını geri çektin.", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = self._load()
        self.giveaway_check.start()
        self.bot.loop.create_task(self._register_view())

    async def _register_view(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(GiveawayView(self))

    def cog_unload(self):
        self.giveaway_check.cancel()

    def _load(self):
        if G_FILE.exists():
            try:
                return json.loads(G_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _save(self):
        def _write():
            G_FILE.parent.mkdir(exist_ok=True, parents=True)
            G_FILE.write_text(json.dumps(self.giveaways, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    def _parse_time(self, time_str):
        time_str = str(time_str).lower().strip()
        birim_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            birim = time_str[-1]
            if birim in birim_map:
                return int(time_str[:-1]) * birim_map[birim]
            return int(time_str)
        except Exception:
            return None

    @commands.hybrid_command(name="çekiliş-başlat", aliases=["giveaway", "gstart"], description="Yeni bir çekiliş başlatır.")
    @commands.has_permissions(manage_guild=True)
    async def giveaway_start(self, ctx, sure: str, *, odul: str):
        """Belirtilen süre boyunca aktif kalacak ödüllü bir çekiliş düzenler."""
        saniye = self._parse_time(sure)
        if not saniye or saniye <= 0:
            return await ctx.send("❌ Geçersiz süre formatı! Örnek: `/çekiliş-başlat sure: 10m odul: Nitro` (s: saniye, m: dakika, h: saat, d: gün)")

        end_time = datetime.utcnow().timestamp() + saniye
        embed = discord.Embed(
            title="🎉 Çekiliş Başladı!",
            description=f"Ödül: **{odul}**\nSona Erme: <t:{int(end_time)}:R>\nKatılımcı Sayısı: **0**",
            color=discord.Color.gold()
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        view = GiveawayView(self)
        msg = await ctx.send(embed=embed, view=view)

        self.giveaways[str(msg.id)] = {
            "message_id": msg.id,
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "prize": odul,
            "end_time": end_time,
            "participants": [],
            "ended": False
        }
        await self._save()

    @tasks.loop(seconds=10)
    async def giveaway_check(self):
        now = datetime.utcnow().timestamp()
        degisti = False
        for mid, g in list(self.giveaways.items()):
            if g.get("ended", False):
                continue
            if now >= g["end_time"]:
                g["ended"] = True
                degisti = True
                await self.end_giveaway(mid, g)
        if degisti:
            await self._save()

    @giveaway_check.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    async def end_giveaway(self, mid, g):
        guild = self.bot.get_guild(int(g["guild_id"]))
        if not guild:
            return
        channel = guild.get_channel(int(g["channel_id"]))
        if not channel:
            return

        try:
            message = await channel.fetch_message(int(mid))
        except Exception:
            return

        participants = g["participants"]
        if not participants:
            embed = discord.Embed(
                title="❌ Çekiliş Sona Erdi",
                description=f"Ödül: **{g['prize']}**\nKatılım olmadığı için kazanan seçilemedi.",
                color=discord.Color.red()
            )
            await message.edit(embed=embed, view=None)
            await channel.send(f"❌ **{g['prize']}** çekilişine katılım olmadığı için kazanan seçilemedi.")
            return

        winner_id = random.choice(participants)
        try:
            winner = guild.get_member(winner_id) or await self.bot.fetch_user(winner_id)
        except Exception:
            winner = None

        winner_mention = winner.mention if winner else f"<@{winner_id}>"

        embed = discord.Embed(
            title="🎉 Çekiliş Sona Erdi!",
            description=f"Ödül: **{g['prize']}**\nKazanan: {winner_mention}\nToplam Katılımcı: **{len(participants)}**",
            color=discord.Color.green()
        )
        await message.edit(embed=embed, view=None)
        await channel.send(f"🎊 Tebrikler {winner_mention}! **{g['prize']}** çekilişini kazandın!")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))

# Yusuf Cebeci @58tc
