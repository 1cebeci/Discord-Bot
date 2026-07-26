import io
import discord
from colorama import Fore, Style, init

init(autoreset=True)

def print_add(message):
    print(f'{Fore.GREEN}[+]{Style.RESET_ALL} {message}')

def print_delete(message):
    print(f'{Fore.RED}[-]{Style.RESET_ALL} {message}')

def print_warning(message):
    print(f'{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}')

def print_error(message):
    print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {message}')


class Clone:
    @staticmethod
    async def roles_delete(guild_to: discord.Guild):
        for role in guild_to.roles:
            try:
                if role.name != "@everyone" and role.position < guild_to.me.top_role.position:
                    await role.delete()
                    print_delete(f"Deleted Role: {role.name}")
            except Exception as e:
                print_error(f"Error deleting role {role.name}: {e}")

    @staticmethod
    async def roles_create(guild_to: discord.Guild, guild_from: discord.Guild):
        roles = [r for r in guild_from.roles if r.name != "@everyone"]
        roles.reverse()
        for role in roles:
            try:
                await guild_to.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                print_add(f"Created Role: {role.name}")
            except Exception as e:
                print_error(f"Error creating role {role.name}: {e}")

    @staticmethod
    async def channels_delete(guild_to: discord.Guild):
        for channel in guild_to.channels:
            try:
                await channel.delete()
                print_delete(f"Deleted Channel: {channel.name}")
            except Exception as e:
                print_error(f"Error deleting channel {channel.name}: {e}")

    @staticmethod
    async def categories_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for category in guild_from.categories:
            try:
                overwrites_to = {}
                for key, value in category.overwrites.items():
                    if isinstance(key, discord.Role):
                        role = discord.utils.get(guild_to.roles, name=key.name)
                        if role:
                            overwrites_to[role] = value
                new_cat = await guild_to.create_category(
                    name=category.name,
                    overwrites=overwrites_to
                )
                await new_cat.edit(position=category.position)
                print_add(f"Created Category: {category.name}")
            except Exception as e:
                print_error(f"Error creating category {category.name}: {e}")

    @staticmethod
    async def channels_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for channel_text in guild_from.text_channels:
            try:
                category = None
                if channel_text.category:
                    category = discord.utils.get(guild_to.categories, name=channel_text.category.name)

                overwrites_to = {}
                for key, value in channel_text.overwrites.items():
                    if isinstance(key, discord.Role):
                        role = discord.utils.get(guild_to.roles, name=key.name)
                        if role:
                            overwrites_to[role] = value

                await guild_to.create_text_channel(
                    name=channel_text.name,
                    overwrites=overwrites_to,
                    position=channel_text.position,
                    topic=channel_text.topic,
                    slowmode_delay=channel_text.slowmode_delay,
                    nsfw=channel_text.nsfw,
                    category=category
                )
                print_add(f"Created Text Channel: {channel_text.name}")
            except Exception as e:
                print_error(f"Error creating text channel {channel_text.name}: {e}")

        for channel_voice in guild_from.voice_channels:
            try:
                category = None
                if channel_voice.category:
                    category = discord.utils.get(guild_to.categories, name=channel_voice.category.name)

                overwrites_to = {}
                for key, value in channel_voice.overwrites.items():
                    if isinstance(key, discord.Role):
                        role = discord.utils.get(guild_to.roles, name=key.name)
                        if role:
                            overwrites_to[role] = value

                await guild_to.create_voice_channel(
                    name=channel_voice.name,
                    overwrites=overwrites_to,
                    position=channel_voice.position,
                    bitrate=channel_voice.bitrate,
                    user_limit=channel_voice.user_limit,
                    category=category
                )
                print_add(f"Created Voice Channel: {channel_voice.name}")
            except Exception as e:
                print_error(f"Error creating voice channel {channel_voice.name}: {e}")

    @staticmethod
    async def emojis_delete(guild_to: discord.Guild):
        for emoji in guild_to.emojis:
            try:
                await emoji.delete()
                print_delete(f"Deleted Emoji: {emoji.name}")
            except Exception as e:
                print_error(f"Error deleting emoji {emoji.name}: {e}")

    @staticmethod
    async def emojis_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for emoji in guild_from.emojis:
            try:
                emoji_bytes = await emoji.read()
                await guild_to.create_custom_emoji(
                    name=emoji.name,
                    image=emoji_bytes
                )
                print_add(f"Created Emoji: {emoji.name}")
            except Exception as e:
                print_error(f"Error creating emoji {emoji.name}: {e}")

    @staticmethod
    async def stickers_delete(guild_to: discord.Guild):
        for sticker in guild_to.stickers:
            try:
                await sticker.delete()
                print_delete(f"Deleted Sticker: {sticker.name}")
            except Exception as e:
                print_error(f"Error deleting sticker {sticker.name}: {e}")

    @staticmethod
    async def stickers_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for sticker in guild_from.stickers:
            try:
                sticker_bytes = await sticker.read()
                file = discord.File(fp=io.BytesIO(sticker_bytes), filename=f"{sticker.name}.png")
                emoji_tag = sticker.emoji if hasattr(sticker, 'emoji') and sticker.emoji else "😀"
                await guild_to.create_sticker(
                    name=sticker.name,
                    description=sticker.description if sticker.description else "Cloned Sticker",
                    emoji=emoji_tag,
                    file=file
                )
                print_add(f"Created Sticker: {sticker.name}")
            except Exception as e:
                print_error(f"Error creating sticker {sticker.name}: {e}")

    @staticmethod
    async def guild_edit(guild_to: discord.Guild, guild_from: discord.Guild):
        try:
            icon_bytes = None
            if guild_from.icon:
                try:
                    icon_bytes = await guild_from.icon.read()
                except Exception as e:
                    print_error(f"Could not fetch icon: {e}")

            await guild_to.edit(name=guild_from.name)
            if icon_bytes:
                await guild_to.edit(icon=icon_bytes)
                print_add(f"Updated Guild Icon: {guild_to.name}")
        except Exception as e:
            print_error(f"Error updating guild info: {e}")

# Yusuf Cebeci @58tc
