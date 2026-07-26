import discord
from discord.ext import commands
import os
import asyncio
import logging
import traceback
import sys
from pathlib import Path
from flask import Flask
from threading import Thread

current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("discord_bot")

app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve çalışıyor."

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = Thread(target=run)
    server_thread.daemon = True
    server_thread.start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c!", intents=intents, help_command=None)
bot.first_ready = True

async def load_extensions():
    cogs = [
        "moderation", "security", "leveling", "giveaway",
        "help", "settings", "utility", "welcome", "fun", "voice", "wordfilter"
    ]
    for cog in cogs:
        try:
            try:
                await bot.load_extension(f"cogs.{cog}")
            except commands.ExtensionAlreadyLoaded:
                continue  # Zaten yuklu, atla
            except (commands.ExtensionNotFound, ModuleNotFoundError):
                try:
                    await bot.load_extension(cog)
                except commands.ExtensionAlreadyLoaded:
                    continue
            logger.info(f"Modul yuklendi: {cog}")
        except Exception:
            logger.error(f"Modul yuklenirken hata olustu ({cog}):\n{traceback.format_exc()}")

@bot.event
async def on_ready():
    if bot.first_ready:
        bot.first_ready = False
        try:
            await bot.tree.sync()
            logger.info("Uygulama (Slash) komutları senkronize edildi.")
        except Exception:
            logger.error(f"Slash komut senkronizasyon hatası:\n{traceback.format_exc()}")

        await bot.change_presence(activity=discord.Game(name="🛡️ c!yardım | v2.0"))
        logger.info(f"{bot.user} başarıyla bağlandı. Sunucu sayısı: {len(bot.guilds)}")
    else:
        logger.info("Bot bağlantısı yenilendi.")

@bot.event
async def on_disconnect():
    logger.warning("Discord bağlantısı koptu, yeniden deneniyor...")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f"Komut hatası ({ctx.command}): {error}")

async def start():
    keep_alive()

    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.critical("BOT_TOKEN ortam değişkeni eksik!")
        return

    retry_count = 0
    async with bot:
        await load_extensions()
        while True:
            try:
                await bot.start(token, reconnect=True)
                break
            except discord.LoginFailure:
                logger.critical("Giriş başarısız, token geçersiz!")
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    wait_time = min(30 * (2 ** retry_count), 300)
                    logger.warning(f"Discord rate limit (429) algılandı! {wait_time} saniye bekleniyor... (Deneme: {retry_count + 1})")
                    await asyncio.sleep(wait_time)
                    retry_count += 1
                else:
                    logger.critical(f"Bot başlatılırken beklenmedik HTTP hatası:\n{traceback.format_exc()}")
                    break
            except Exception:
                logger.critical(f"Bot başlatılırken beklenmedik hata:\n{traceback.format_exc()}")
                break

if __name__ == "__main__":
    asyncio.run(start())

# Yusuf Cebeci @58tc

