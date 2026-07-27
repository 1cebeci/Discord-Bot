import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

DATA_FILE = "confession_settings.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def get_guild_settings(guild_id):
    data = load_data()
    gid = str(guild_id)
    if gid not in data:
        data[gid] = {
            "channel_id": None,
            "log_channel_id": None,
            "approval_enabled": False,
            "count": 0,
            "embed_color": 0x5865F2
        }
        save_data(data)
    return data[gid]

def update_guild_setting(guild_id, key, value):
    data = load_data()
    gid = str(guild_id)
    if gid not in data:
        data[gid] = {
            "channel_id": None,
            "log_channel_id": None,
            "approval_enabled": False,
            "count": 0,
            "embed_color": 0x5865F2
        }
    data[gid][key] = value
    save_data(data)

def increment_count(guild_id):
    data = load_data()
    gid = str(guild_id)
    if gid in data:
        data[gid]["count"] = data[gid].get("count", 0) + 1
        save_data(data)
        return data[gid]["count"]
    return 1


class ConfessionModal(discord.ui.Modal, title="Anonim İtiraf Formu"):
    title_input = discord.ui.TextInput(
        label="İtiraf Başlığı (Opsiyonel)",
        placeholder="Örn: İçimde Kalmasın...",
        required=False,
        max_length=100
    )
    confession_input = discord.ui.TextInput(
        label="İtirafınız",
        placeholder="İtiraf etmek istediğiniz şeyi yazın. Kimliğiniz tamamen gizli tutulur.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Bu işlem sadece sunucuda yapılabilir.", ephemeral=True)
            return

        settings = get_guild_settings(guild.id)
        channel_id = settings.get("channel_id")
        if not channel_id:
            await interaction.response.send_message("❌ İtiraf kanalı henüz ayarlanmamış!", ephemeral=True)
            return

        target_channel = guild.get_channel(int(channel_id))
        if not target_channel:
            await interaction.response.send_message("❌ İtiraf kanalı bulunamadı.", ephemeral=True)
            return

        approval_enabled = settings.get("approval_enabled", False)
        log_channel_id = settings.get("log_channel_id")

        title_text = self.title_input.value.strip() or "Anonim İtiraf"
        confession_text = self.confession_input.value.strip()

        if approval_enabled and log_channel_id:
            log_channel = guild.get_channel(int(log_channel_id))
            if log_channel:
                embed = discord.Embed(
                    title=f"⏳ Onay Bekleyen İtiraf: {title_text}",
                    description=confession_text,
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.set_author(name=f"Gönderen: {interaction.user} (ID: {interaction.user.id})", icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text="Yetkili Onayı Bekleniyor")

                view = ConfessionApprovalView(
                    user_id=interaction.user.id,
                    title_text=title_text,
                    confession_text=confession_text,
                    target_channel_id=int(channel_id)
                )
                await log_channel.send(embed=embed, view=view)
                await interaction.response.send_message("✅ İtirafınız yetkili onayına gönderildi!", ephemeral=True)
                return

        count = increment_count(guild.id)
        color = settings.get("embed_color", 0x5865F2)

        embed = discord.Embed(
            title=f"🤫 İtiraf #{count} - {title_text}",
            description=confession_text,
            color=discord.Color(color),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text="Anonim İtiraf • Gizlilik Korunmaktadır")

        await target_channel.send(embed=embed)
        await interaction.response.send_message("✅ İtirafınız anonim olarak paylaşıldı!", ephemeral=True)


class ConfessionReplyModal(discord.ui.Modal, title="İtirafa Anonim Yanıt"):
    number_input = discord.ui.TextInput(
        label="İtiraf Numarası",
        placeholder="Örn: 5 (Sadece numara girin)",
        required=True,
        max_length=10
    )
    reply_input = discord.ui.TextInput(
        label="Yanıtınız",
        placeholder="Vereceğiniz anonim yanıtı buraya yazın.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        num_str = self.number_input.value.strip().replace("#", "")
        if not num_str.isdigit():
            await interaction.response.send_message("❌ Lütfen geçerli bir numara girin (Örn: 5).", ephemeral=True)
            return

        settings = get_guild_settings(guild.id)
        channel_id = settings.get("channel_id")
        if not channel_id:
            await interaction.response.send_message("❌ İtiraf kanalı bulunamadı.", ephemeral=True)
            return

        target_channel = guild.get_channel(int(channel_id))
        if not target_channel:
            await interaction.response.send_message("❌ İtiraf kanalı bulunamadı.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"💬 İtiraf #{num_str}'e Anonim Yanıt",
            description=self.reply_input.value.strip(),
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text="Anonim Yanıt")

        await target_channel.send(embed=embed)
        await interaction.response.send_message("✅ Yanıtınız anonim olarak gönderildi!", ephemeral=True)


class ConfessionApprovalView(discord.ui.View):
    def __init__(self, user_id, title_text, confession_text, target_channel_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.title_text = title_text
        self.confession_text = confession_text
        self.target_channel_id = target_channel_id

    @discord.ui.button(label="Onayla ve Yayınla", style=discord.ButtonStyle.success, emoji="✅", custom_id="confession_approve_btn")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        target_channel = guild.get_channel(self.target_channel_id)
        if not target_channel:
            await interaction.response.send_message("İtiraf kanalı bulunamadı.", ephemeral=True)
            return

        count = increment_count(guild.id)
        settings = get_guild_settings(guild.id)
        color = settings.get("embed_color", 0x5865F2)

        embed = discord.Embed(
            title=f"🤫 İtiraf #{count} - {self.title_text}",
            description=self.confession_text,
            color=discord.Color(color),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text="Anonim İtiraf • Onaylandı")

        await target_channel.send(embed=embed)

        for child in self.children:
            child.disabled = True
        
        orig_embed = interaction.message.embeds[0]
        orig_embed.color = discord.Color.green()
        orig_embed.title = f"✅ ONAYLANDI (İtiraf #{count})"
        orig_embed.set_footer(text=f"Onaylayan: {interaction.user}")

        await interaction.response.edit_message(embed=orig_embed, view=self)

    @discord.ui.button(label="Reddet", style=discord.ButtonStyle.danger, emoji="❌", custom_id="confession_reject_btn")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True

        orig_embed = interaction.message.embeds[0]
        orig_embed.color = discord.Color.red()
        orig_embed.title = "❌ REDDEDİLDİ"
        orig_embed.set_footer(text=f"Reddeden: {interaction.user}")

        await interaction.response.edit_message(embed=orig_embed, view=self)


class ConfessionPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="İtiraf Et", style=discord.ButtonStyle.primary, emoji="🤫", custom_id="confession_make_btn")
    async def make_confession(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessionModal())

    @discord.ui.button(label="İtirafa Yanıt Ver", style=discord.ButtonStyle.secondary, emoji="💬", custom_id="confession_reply_btn")
    async def reply_confession(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessionReplyModal())

    @discord.ui.button(label="Nasıl Çalışır?", style=discord.ButtonStyle.success, emoji="❓", custom_id="confession_info_btn")
    async def show_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        info_embed = discord.Embed(
            title="ℹ️ Anonim İtiraf Sistemi Hakkında",
            description=(
                "• **İtiraf Et** butonuna tıklayarak açılan form üzerinden anonim itiraf yapabilirsiniz.\n"
                "• Kullanıcı adınız veya ID'niz kesinlikle kanalda **gözükmez**.\n"
                "• Belirli bir itirafa cevap vermek için **İtirafa Yanıt Ver** butonunu kullanabilirsiniz.\n"
                "• Saygısızlık ve kural ihlali içeren itiraflar yetkililer tarafından engellenir."
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=info_embed, ephemeral=True)


class Confession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(ConfessionPanelView())

    @commands.hybrid_command(name="itiraf-paneli-kur", description="İtiraf buton panelini belirlenen kanala kurar.")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        itiraf_kanali="İtirafların gönderileceği ve panelin kurulacağı kanal",
        log_kanali="Onay bekleyen itirafların gideceği log kanalı (Opsiyonel)",
        onay_sistemi="Yetkili onayı zorunlu olsun mu?"
    )
    async def setup_panel(
        self,
        ctx: commands.Context,
        itiraf_kanali: discord.TextChannel,
        log_kanali: discord.TextChannel = None,
        onay_sistemi: bool = False
    ):
        update_guild_setting(ctx.guild.id, "channel_id", itiraf_kanali.id)
        if log_kanali:
            update_guild_setting(ctx.guild.id, "log_channel_id", log_kanali.id)
        update_guild_setting(ctx.guild.id, "approval_enabled", onay_sistemi)

        panel_embed = discord.Embed(
            title="🤫 Anonim İtiraf Paneli",
            description=(
                "İçinizde tutmak istemediğiniz tüm düşünceleri, duyguları veya itirafları tam güvenlik ve anonimlikle paylaşabilirsiniz!\n\n"
                "👇 **Aşağıdaki butonları kullanarak işlem yapabilirsiniz:**\n"
                "• **`[🤫 İtiraf Et]`** -> Formu açar ve anonim itirafınızı gönderir.\n"
                "• **`[💬 İtirafa Yanıt Ver]`** -> Belirli bir itirafa cevap vermenizi sağlar.\n"
                "• **`[❓ Nasıl Çalışır?]`** -> Sistem detaylarını gösterir."
            ),
            color=discord.Color.from_rgb(88, 101, 242)
        )
        panel_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        panel_embed.set_footer(text="İtiraflarınız %100 Gizli ve Anonimdir")

        await itiraf_kanali.send(embed=panel_embed, view=ConfessionPanelView())

        info_text = f"✅ İtiraf paneli {itiraf_kanali.mention} kanalında başarıyla kuruldu!"
        if log_kanali:
            info_text += f"\n📋 Yetkili onay logları {log_kanali.mention} kanalına gidecek."
        if onay_sistemi:
            info_text += "\n⚙️ Yetkili onay sistemi **AÇIK**."
        else:
            info_text += "\n⚙️ Yetkili onay sistemi **KAPALI** (İtiraflar doğrudan yayınlanacak)."

        await ctx.send(info_text)

async def setup(bot):
    await bot.add_cog(Confession(bot))
