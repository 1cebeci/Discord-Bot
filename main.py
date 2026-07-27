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

# Yollar
current_dir = Path(__file__).parent.resolve()
sys.path.append(str(current_dir))

# Loglama
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("discord_bot")

# Flask (Keep-Alive)
app = Flask('')
@app.route('/')
def home(): return "Bot aktif."

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c!", intents=intents, help_command=None)

async def load_extensions():
    # Yüklenecek modüller
    cogs = ["leveling", "confession"]
    loaded_count = 0
    failed_count = 0
    
    for cog in cogs:
        try:
            # Önce cogs klasöründe ara, bulamazsa ana dizinde ara
            try:
                await bot.load_extension(f"cogs.{cog}")
            except:
                await bot.load_extension(cog)
            logger.info(f"✅ Modül yüklendi: {cog}")
            loaded_count += 1
        except Exception as e:
            logger.error(f"❌ Modül yüklenemedi ({cog}): {e}")
            traceback.print_exc()
            failed_count += 1
    
    logger.info(f"📊 Yükleme Özeti: {loaded_count} başarılı, {failed_count} başarısız")

@bot.event
async def on_ready():
    # Slash komutlarını senkronize et
    try:
        await bot.tree.sync()
        logger.info("Slash komutları senkronize edildi.")
    except Exception as e:
        logger.error(f"Senkronizasyon hatası: {e}")
    
    logger.info(f"{bot.user} başarıyla giriş yaptı!")

# Prefix komutları için gerekli işlemci
@bot.event
async def on_message(message):
    if message.author.bot: 
        return
    
    logger.debug(f"Mesaj alındı: {message.author} - {message.content}")
    await bot.process_commands(message)

async def start():
    keep_alive()
    token = os.environ.get("BOT_TOKEN")
    
    if not token:
        logger.error("❌ BOT_TOKEN environment variable'ı bulunamadı!")
        return
    
    logger.info("🤖 Bot başlatılıyor...")
    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(start())
