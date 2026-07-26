import discord
from discord.ext import commands
import json
import asyncio
from pathlib import Path

DATA_DIR = Path(__file__).parent.resolve() / "data"
SET_FILE = DATA_DIR / "settings.json"

try:
    from cogs.leveling import default_conf
except ImportError:
    try:
        from leveling import default_conf
    except ImportError:
        def default_conf():
            return {"aktif": False, "kanal": None, "roller": {}}

class TabDropdown(discord.ui.Select):
    def __init__(self, active_tab):
        options = [
            discord.SelectOption(label="Ana Sayfa", value="home", emoji="🏠", description="Genel durum ve özet bilgiler"),
            discord.SelectOption(label="Güvenlik Ayarları", value="security", emoji="🛡️", description="Filtreler ve koruma ayarları"),
            discord.SelectOption(label="Karşılama Ayarları", value="welcome", emoji="👋", description="Giriş/çıkış mesajı ayarları"),
            discord.SelectOption(label="Seviye Ayarları", value="leveling", emoji="📈", description="Seviye sistemi ve rol ödülleri"),
            discord.SelectOption(label="Genel Ayarlar", value="general", emoji="⚙️", description="Log kanalı vb. genel ayarlar")
        ]
        for opt in options:
            if opt.value == active_tab:
                opt.default = True
        super().__init__(placeholder="📂 Kategori seç...", options=options, row=4)

    async def callback(self, interaction: discord.Interaction):
        self.view.tab = self.values[0]
        self.view.rebuild_view()
        embed = await self.view.cog.create_panel_embed(self.view.guild_id, self.view.tab)
        await interaction.response.edit_message(embed=embed, view=self.view)

class RefreshButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Yenile 🔄", style=discord.ButtonStyle.secondary, row=0)

    async def callback(self, interaction: discord.Interaction):
        embed = await self.view.cog.create_panel_embed(self.view.guild_id, self.view.tab)
        await interaction.response.edit_message(embed=embed, view=self.view)

class ToggleButton(discord.ui.Button):
    def __init__(self, key, label, current_val):
        self.key = key
        style = discord.ButtonStyle.green if current_val else discord.ButtonStyle.red
        indicator = "✅" if current_val else "❌"
        super().__init__(label=f"{label}: {indicator}", style=style)

    async def callback(self, interaction: discord.Interaction):
        guild_id = self.view.guild_id
        bot = self.view.bot

        if self.view.tab == "security":
            sec_cog = bot.get_cog("Security")
            if sec_cog:
                cfg = sec_cog._guild_ayar(guild_id)
                cfg[self.key] = not cfg.get(self.key, True)
                await sec_cog._kaydet()
        elif self.view.tab == "welcome":
            w_cog = bot.get_cog("Welcome")
            if w_cog:
                cfg = w_cog._guild_config(guild_id)
                cfg[self.key] = not cfg.get(self.key, False)
                await w_cog._save()
        elif self.view.tab == "leveling":
            lvl_cog = bot.get_cog("Leveling")
            if lvl_cog:
                cfg = lvl_cog.conf.setdefault(guild_id, default_conf())
                cfg[self.key] = not cfg.get(self.key, False)
                await lvl_cog._save_conf()

        self.view.rebuild_view()
        embed = await self.view.cog.create_panel_embed(guild_id, self.view.tab)
        await interaction.response.edit_message(embed=embed, view=self.view)

class WelcomeMsgModal(discord.ui.Modal):
    def __init__(self, w_cog, key, current_val):
        title = "Giriş Mesajını Düzenle" if key == "w_msg" else "Çıkış Mesajını Düzenle"
        super().__init__(title=title)
        self.w_cog = w_cog
        self.key = key
        self.msg_input = discord.ui.TextInput(
            label="Mesaj İçeriği",
            style=discord.TextStyle.long,
            placeholder="Örn: Hoş geldin {üye}!",
            default=current_val,
            max_length=500
        )
        self.add_item(self.msg_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        cfg = self.w_cog._guild_config(guild_id)
        cfg[self.key] = self.msg_input.value
        await self.w_cog._save()
        await interaction.response.send_message("✅ Karşılama mesaj şablonu güncellendi.", ephemeral=True)

class EditMessageButton(discord.ui.Button):
    def __init__(self, key, label):
        self.key = key
        super().__init__(label=label, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        w_cog = self.view.bot.get_cog("Welcome")
        if w_cog:
            cfg = w_cog._guild_config(self.view.guild_id)
            current_val = cfg.get(self.key, "")
            await interaction.response.send_modal(WelcomeMsgModal(w_cog, self.key, current_val))

class WelcomeChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="💬 Karşılama kanalı seç...",
            channel_types=[discord.ChannelType.text],
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        w_cog = self.view.bot.get_cog("Welcome")
        if w_cog:
            cfg = w_cog._guild_config(self.view.guild_id)
            cfg["w_channel"] = str(self.values[0].id)
            await w_cog._save()
            await interaction.response.send_message(f"✅ Karşılama kanalı {self.values[0].mention} olarak ayarlandı.", ephemeral=True)

class LevelingChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="📢 Seviye bildirim kanalı seç...",
            channel_types=[discord.ChannelType.text],
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        lvl_cog = self.view.bot.get_cog("Leveling")
        if lvl_cog:
            cfg = lvl_cog.conf.setdefault(self.view.guild_id, default_conf())
            cfg["kanal"] = str(self.values[0].id)
            await lvl_cog._save_conf()
            await interaction.response.send_message(f"✅ Seviye bildirim kanalı {self.values[0].mention} olarak ayarlandı.", ephemeral=True)

class LogChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="📝 Log kanalı seç...",
            channel_types=[discord.ChannelType.text],
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        cog = self.view.cog
        cog.data.setdefault(self.view.guild_id, {})["log_kanal"] = self.values[0].id
        await cog._save()
        await interaction.response.send_message(f"✅ Güvenlik log kanalı {self.values[0].mention} olarak ayarlandı.", ephemeral=True)

class WhitelistAddModal(discord.ui.Modal):
    def __init__(self, sec_cog):
        super().__init__(title="İzinli Domain Ekle")
        self.sec_cog = sec_cog
        self.domain_input = discord.ui.TextInput(
            label="Domain Adı",
            placeholder="Örn: google.com",
            max_length=100
        )
        self.add_item(self.domain_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        cfg = self.sec_cog._guild_ayar(guild_id)
        domain = self.domain_input.value.lower().strip()
        if domain in cfg["whitelist"]:
            return await interaction.response.send_message(f"⚠️ `{domain}` zaten izinli listede.", ephemeral=True)
        cfg["whitelist"].append(domain)
        await self.sec_cog._kaydet()
        await interaction.response.send_message(f"✅ `{domain}` izinli listeden muaf tutuldu.", ephemeral=True)

class AddWhitelistButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➕ İzinli Ekle", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        sec_cog = self.view.bot.get_cog("Security")
        if sec_cog:
            await interaction.response.send_modal(WhitelistAddModal(sec_cog))

class RemoveWhitelistSelect(discord.ui.Select):
    def __init__(self, sec_cog, whitelist):
        options = [discord.SelectOption(label=d, value=d) for d in whitelist[:25]] or [discord.SelectOption(label="İzinli domain yok", value="none")]
        super().__init__(placeholder="🗑️ Silinecek domaini seç...", options=options)
        self.sec_cog = sec_cog

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return await interaction.response.send_message("Silinecek domain yok.", ephemeral=True)
        guild_id = str(interaction.guild.id)
        cfg = self.sec_cog._guild_ayar(guild_id)
        if self.values[0] in cfg["whitelist"]:
            cfg["whitelist"].remove(self.values[0])
            await self.sec_cog._kaydet()
            await interaction.response.send_message(f"🗑️ `{self.values[0]}` listeden silindi.", ephemeral=True)

class RemoveWhitelistView(discord.ui.View):
    def __init__(self, sec_cog, whitelist):
        super().__init__(timeout=60)
        self.add_item(RemoveWhitelistSelect(sec_cog, whitelist))

class RemoveWhitelistButton(discord.ui.Button):
    def __init__(self, whitelist):
        super().__init__(label="🗑️ İzinli Sil", style=discord.ButtonStyle.danger)
        self.whitelist = whitelist

    async def callback(self, interaction: discord.Interaction):
        sec_cog = self.view.bot.get_cog("Security")
        if sec_cog:
            if not self.whitelist:
                return await interaction.response.send_message("❌ İzinli domain listesi zaten boş.", ephemeral=True)
            await interaction.response.send_message(view=RemoveWhitelistView(sec_cog, self.whitelist), ephemeral=True)

class LevelRewardModal(discord.ui.Modal):
    def __init__(self, lvl_cog):
        super().__init__(title="Rol Ödülü Belirle")
        self.lvl_cog = lvl_cog
        self.lvl_input = discord.ui.TextInput(
            label="Hedef Seviye",
            placeholder="Örn: 5",
            max_length=3
        )
        self.add_item(self.lvl_input)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.lvl_input.value.isdigit():
            return await interaction.response.send_message("❌ Seviye sadece sayı olmalıdır.", ephemeral=True)
        lvl = int(self.lvl_input.value)
        view = LevelRewardRoleSelectView(self.lvl_cog, lvl)
        await interaction.response.send_message(f"**Seviye {lvl}** ödülü olarak verilecek rolü seçin:", view=view, ephemeral=True)

class LevelRewardRoleSelectView(discord.ui.View):
    def __init__(self, lvl_cog, lvl):
        super().__init__(timeout=60)
        self.lvl_cog = lvl_cog
        self.lvl = lvl

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Bir rol seç...")
    async def select_role(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        rol = select.values[0]
        guild_id = str(interaction.guild.id)
        cfg = self.lvl_cog.conf.setdefault(guild_id, default_conf())
        cfg.setdefault("roller", {})
        cfg["roller"][str(self.lvl)] = rol.id
        await self.lvl_cog._save_conf()
        await interaction.response.edit_message(content=f"✅ **Seviye {self.lvl}** ödülü olarak {rol.mention} rolü ayarlandı.", view=None)

class AddRewardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➕ Ödül Ekle", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        lvl_cog = self.view.bot.get_cog("Leveling")
        if lvl_cog:
            await interaction.response.send_modal(LevelRewardModal(lvl_cog))

class RemoveRewardSelect(discord.ui.Select):
    def __init__(self, lvl_cog, roller):
        options = [
            discord.SelectOption(label=f"Seviye {lvl}", value=lvl, description=f"Rol ID: {rid}")
            for lvl, rid in sorted(roller.items(), key=lambda x: int(x[0]))
        ][:25] or [discord.SelectOption(label="Seviye ödülü bulunmuyor", value="none")]
        super().__init__(placeholder="🗑️ Silinecek seviye ödülünü seç...", options=options)
        self.lvl_cog = lvl_cog

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return await interaction.response.send_message("Silinecek ödül yok.", ephemeral=True)
        guild_id = str(interaction.guild.id)
        if guild_id in self.lvl_cog.conf and "roller" in self.lvl_cog.conf[guild_id]:
            self.lvl_cog.conf[guild_id]["roller"].pop(self.values[0], None)
            await self.lvl_cog._save_conf()
            await interaction.response.send_message(f"🗑️ Seviye {self.values[0]} ödülü silindi.", ephemeral=True)

class RemoveRewardView(discord.ui.View):
    def __init__(self, lvl_cog, roller):
        super().__init__(timeout=60)
        self.add_item(RemoveRewardSelect(lvl_cog, roller))

class RemoveRewardButton(discord.ui.Button):
    def __init__(self, roller):
        super().__init__(label="🗑️ Ödül Sil", style=discord.ButtonStyle.danger)
        self.roller = roller

    async def callback(self, interaction: discord.Interaction):
        lvl_cog = self.view.bot.get_cog("Leveling")
        if lvl_cog:
            if not self.roller:
                return await interaction.response.send_message("❌ Seviye rol ödülü bulunmuyor.", ephemeral=True)
            await interaction.response.send_message(view=RemoveRewardView(lvl_cog, self.roller), ephemeral=True)

class ControlPanelView(discord.ui.View):
    def __init__(self, bot, cog, guild_id, user_id, initial_tab="home"):
        super().__init__(timeout=300)
        self.bot = bot
        self.cog = cog
        self.guild_id = str(guild_id)
        self.user_id = user_id
        self.tab = initial_tab
        self.rebuild_view()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Bu paneli sadece komutu kullanan yönetici kontrol edebilir.", ephemeral=True)
            return False
        return True

    def rebuild_view(self):
        self.clear_items()
        self.add_item(TabDropdown(self.tab))

        sec_cog = self.bot.get_cog("Security")
        w_cog = self.bot.get_cog("Welcome")
        lvl_cog = self.bot.get_cog("Leveling")

        if self.tab == "home":
            self.add_item(RefreshButton())
        elif self.tab == "security":
            if sec_cog:
                cfg = sec_cog._guild_ayar(self.guild_id)
                self.add_item(ToggleButton("link", "Link Engeli", cfg.get("link", True)))
                self.add_item(ToggleButton("kufur", "Küfür Engeli", cfg.get("kufur", True)))
                self.add_item(ToggleButton("reklam", "Reklam Engeli", cfg.get("reklam", True)))
                self.add_item(ToggleButton("spam", "Spam Engeli", cfg.get("spam", True)))
                self.add_item(ToggleButton("caps", "Caps Engeli", cfg.get("caps", True)))
                self.add_item(AddWhitelistButton())
                self.add_item(RemoveWhitelistButton(cfg.get("whitelist", [])))
        elif self.tab == "welcome":
            if w_cog:
                cfg = w_cog._guild_config(self.guild_id)
                self.add_item(ToggleButton("w_aktif", "Hoş Geldin Mesajı", cfg.get("w_aktif", False)))
                self.add_item(ToggleButton("l_aktif", "Görüşürüz Mesajı", cfg.get("l_aktif", False)))
                self.add_item(WelcomeChannelSelect())
                self.add_item(EditMessageButton("w_msg", "Giriş Mesajını Düzenle"))
                self.add_item(EditMessageButton("l_msg", "Çıkış Mesajını Düzenle"))
        elif self.tab == "leveling":
            if lvl_cog:
                cfg = lvl_cog.conf.get(self.guild_id, default_conf())
                self.add_item(ToggleButton("aktif", "Seviye Sistemi", cfg.get("aktif", False)))
                self.add_item(LevelingChannelSelect())
                self.add_item(AddRewardButton())
                self.add_item(RemoveRewardButton(cfg.get("roller", {})))
        elif self.tab == "general":
            self.add_item(LogChannelSelect())

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self._load()

    def _load(self):
        if SET_FILE.exists():
            try:
                return json.loads(SET_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    async def _save(self):
        def _write():
            SET_FILE.parent.mkdir(exist_ok=True, parents=True)
            SET_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        await asyncio.to_thread(_write)

    async def create_panel_embed(self, guild_id, tab):
        guild_id = str(guild_id)
        guild = self.bot.get_guild(int(guild_id))
        guild_name = guild.name if guild else "Sunucu"

        sec_cog = self.bot.get_cog("Security")
        w_cog = self.bot.get_cog("Welcome")
        lvl_cog = self.bot.get_cog("Leveling")

        embed = discord.Embed(color=0x2f3136)
        if guild and guild.icon:
            embed.set_author(name=f"{guild_name} Yönetim Paneli", icon_url=guild.icon.url)
        else:
            embed.set_author(name=f"{guild_name} Yönetim Paneli")

        def status_str(b):
            return "✅ **Açık**" if b else "❌ **Kapalı**"

        if tab == "home":
            embed.title = "🏠 Sunucu Genel Durumu"
            embed.description = "Aktif bot sistemlerinin durumu ve temel konfigürasyonu aşağıda gösterilmektedir."

            if sec_cog:
                s_cfg = sec_cog._guild_ayar(guild_id)
                sec_status = (
                    f"🔗 Link Engeli: {status_str(s_cfg.get('link', True))}\n"
                    f"🤬 Küfür Engeli: {status_str(s_cfg.get('kufur', True))}\n"
                    f"📢 Reklam Engeli: {status_str(s_cfg.get('reklam', True))}\n"
                    f"🛡️ Spam Engeli: {status_str(s_cfg.get('spam', True))}\n"
                    f"🔠 Caps Engeli: {status_str(s_cfg.get('caps', True))}"
                )
                embed.add_field(name="🛡️ Güvenlik Filtreleri", value=sec_status, inline=False)

            if w_cog:
                w_cfg = w_cog._guild_config(guild_id)
                w_chan = f"<#{w_cfg.get('w_channel')}>" if w_cfg.get("w_channel") else "*Belirlenmedi*"
                w_status = (
                    f"📥 Hoş Geldin Bildirimi: {status_str(w_cfg.get('w_aktif', False))}\n"
                    f"📤 Görüşürüz Bildirimi: {status_str(w_cfg.get('l_aktif', False))}\n"
                    f"💬 Karşılama Kanalı: {w_chan}"
                )
                embed.add_field(name="👋 Karşılama Ayarları", value=w_status, inline=False)

            if lvl_cog:
                l_cfg = lvl_cog.conf.get(guild_id, default_conf())
                l_chan = f"<#{l_cfg.get('kanal')}>" if l_cfg.get("kanal") else "*Ayarlanmadı (Kanalda bildirilmez)*"
                l_status = (
                    f"📈 Seviye Sistemi: {status_str(l_cfg.get('aktif', False))}\n"
                    f"📢 Seviye Kanalı: {l_chan}\n"
                    f"🎁 Rol Ödülü Sayısı: **{len(l_cfg.get('roller', {}))}**"
                )
                embed.add_field(name="📈 Seviye Sistemi", value=l_status, inline=False)

            gen_cfg = self.data.get(guild_id, {})
            log_chan = f"<#{gen_cfg.get('log_kanal')}>" if gen_cfg.get("log_kanal") else "*Belirlenmedi*"
            embed.add_field(name="⚙️ Genel Ayarlar", value=f"📝 Log Kanalı: {log_chan}", inline=False)

        elif tab == "security":
            embed.title = "🛡️ Güvenlik Filtreleri"
            embed.description = "Sunucunuzun güvenliğini artırmak için gerekli koruma ayarlarını buradan yapabilirsiniz."
            if sec_cog:
                s_cfg = sec_cog._guild_ayar(guild_id)
                embed.add_field(name="🔗 Link Engeli", value=status_str(s_cfg.get('link', True)), inline=True)
                embed.add_field(name="🤬 Küfür Engeli", value=status_str(s_cfg.get('kufur', True)), inline=True)
                embed.add_field(name="📢 Reklam Engeli", value=status_str(s_cfg.get('reklam', True)), inline=True)
                embed.add_field(name="🛡️ Spam Engeli", value=status_str(s_cfg.get('spam', True)), inline=True)
                embed.add_field(name="🔠 Caps Engeli", value=status_str(s_cfg.get('caps', True)), inline=True)
                whitelist_str = ", ".join(f"`{d}`" for d in s_cfg.get('whitelist', [])) if s_cfg.get('whitelist') else "*Beyaz liste boş*"
                embed.add_field(name="✅ İzinli Domainler (Beyaz Liste)", value=whitelist_str, inline=False)

        elif tab == "welcome":
            embed.title = "👋 Karşılama Sistemi Ayarları"
            embed.description = "Üye giriş ve çıkış bildirimlerini özelleştirin."
            if w_cog:
                w_cfg = w_cog._guild_config(guild_id)
                embed.add_field(name="Hoş Geldin Bildirimi", value=status_str(w_cfg.get('w_aktif', False)), inline=True)
                embed.add_field(name="Görüşürüz Bildirimi", value=status_str(w_cfg.get('l_aktif', False)), inline=True)
                w_chan = f"<#{w_cfg.get('w_channel')}>" if w_cfg.get("w_channel") else "*Kanal atanmadı*"
                embed.add_field(name="Gönderim Kanalı", value=w_chan, inline=True)
                embed.add_field(name="📥 Hoş Geldin Şablonu", value=f"```{w_cfg.get('w_msg')}```", inline=False)
                embed.add_field(name="📤 Görüşürüz Şablonu", value=f"```{w_cfg.get('l_msg')}```", inline=False)
                embed.set_footer(text="Değişkenler: {üye} = Bahsetme, {sayı} = Üye Sayısı")

        elif tab == "leveling":
            embed.title = "📈 Seviye Sistemi Konfigürasyonu"
            embed.description = "Seviye sistemi ayarlarını ve rol ödüllerini yönetin."
            if lvl_cog:
                l_cfg = lvl_cog.conf.get(guild_id, default_conf())
                embed.add_field(name="Seviye Sistemi", value=status_str(l_cfg.get('aktif', False)), inline=True)
                l_chan = f"<#{l_cfg.get('kanal')}>" if l_cfg.get("kanal") else "*Kanal atanmadı*"
                embed.add_field(name="Bildirim Kanalı", value=l_chan, inline=True)
                
                rewards_list = []
                for lvl, rid in sorted(l_cfg.get('roller', {}).items(), key=lambda x: int(x[0])):
                    rewards_list.append(f"• **Seviye {lvl}** ➔ <@&{rid}>")
                rewards_str = "\n".join(rewards_list) if rewards_list else "*Rol ödülü bulunmuyor*"
                embed.add_field(name="🎁 Seviye Rol Ödülleri", value=rewards_str, inline=False)

        elif tab == "general":
            embed.title = "⚙️ Genel Ayarlar"
            embed.description = "Botun sunucuya özel genel ayarları."
            gen_cfg = self.data.get(guild_id, {})
            log_chan = f"<#{gen_cfg.get('log_kanal')}>" if gen_cfg.get("log_kanal") else "*Log kanalı atanmadı*"
            embed.add_field(name="📝 Güvenlik Log Kanalı", value=log_chan, inline=False)

        return embed

    @commands.hybrid_command(name="panel", aliases=["kontrolpaneli", "cp"], description="Botun gelişmiş yönetim panelini açar.")
    @commands.has_permissions(administrator=True)
    async def panel(self, ctx, sekme: str = "home"):
        """Gelişmiş yönetim panelini açarak bot ayarlarını butonlarla yönetmenizi sağlar."""
        tab = sekme.lower().strip()
        valid_tabs = ["home", "security", "welcome", "leveling", "general"]
        if tab not in valid_tabs:
            tab = "home"
        
        embed = await self.create_panel_embed(ctx.guild.id, tab)
        view = ControlPanelView(self.bot, self, ctx.guild.id, ctx.author.id, initial_tab=tab)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Settings(bot))

# Yusuf Cebeci @58tc
