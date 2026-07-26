import os
import sys
import platform
import asyncio
from colorama import Fore, Style, init
import discord
from serverclone import Clone

init(autoreset=True)

try:
    from pypresence import Presence
    RPC = Presence('891955385903226880')
    RPC.connect()
    RPC.update(state="Cloning Server...", details="Server Cloner")
except Exception:
    RPC = None

mytitle = "Server Cloner Tool"

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
        os.system(f"title {mytitle}")
    else:
        os.system("clear")

clear_screen()

print(f"""{Fore.CYAN}
  ██████╗██╗      ██████╗ ███╗   ██╗███████╗██████╗
 ██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝██╔══██╗
 ██║     ██║     ██║   ██║██╔██╗ ██║█████╗  ██████╔╝
 ██║     ██║     ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗
 ╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗██║  ██║
  ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝{Style.RESET_ALL}
""")

token = input("Lütfen Token girin:\n > ").strip()
guild_s = input("Kopyalanacak (Kaynak) Sunucu ID:\n > ").strip()
guild = input("Kopyalanacak (Hedef) Sunucu ID:\n > ").strip()

print(f"\n{Fore.YELLOW}=== Kopyalama Seçenekleri ==={Style.RESET_ALL}")
print(" [1] Full Klonlama (Roller, Kanallar, Emojiler, Çıkartmalar)")
print(" [2] Sadece Roller")
print(" [3] Sadece Kanallar ve Kategoriler")
print(" [4] Sadece Emojiler")
print(" [5] Sadece Çıkartmalar")
print(" [6] Sadece Emojiler ve Çıkartmalar (Emoji + Sticker)")
print(" [7] Özel Seçim (Tek tek evet/hayır ile seç)")

choice = input("\nSeçiminiz (1-7): ").strip()

clone_roles = False
clone_channels = False
clone_emojis = False
clone_stickers = False

if choice == "1":
    clone_roles = clone_channels = clone_emojis = clone_stickers = True
elif choice == "2":
    clone_roles = True
elif choice == "3":
    clone_channels = True
elif choice == "4":
    clone_emojis = True
elif choice == "5":
    clone_stickers = True
elif choice == "6":
    clone_emojis = clone_stickers = True
elif choice == "7":
    clone_roles = input("Roller klonlansın mı? (e/h): ").strip().lower() == 'e'
    clone_channels = input("Kanallar klonlansın mı? (e/h): ").strip().lower() == 'e'
    clone_emojis = input("Emojiler klonlansın mı? (e/h): ").strip().lower() == 'e'
    clone_stickers = input("Çıkartmalar klonlansın mı? (e/h): ").strip().lower() == 'e'
else:
    print(f"{Fore.YELLOW}[!] Geçersiz seçim yapıldı, varsayılan olarak hepsi seçildi.{Style.RESET_ALL}")
    clone_roles = clone_channels = clone_emojis = clone_stickers = True

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n{Fore.GREEN}[+] Giriş Yapıldı: {client.user}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Seçilen Kopyalama İşlemleri Başlatılıyor...{Style.RESET_ALL}\n")
    
    guild_from = client.get_guild(int(guild_s))
    guild_to = client.get_guild(int(guild))
    
    if not guild_from or not guild_to:
        print(f"{Fore.RED}[!] Belirtilen sunucu ID'lerinden biri bulunamadı. Botun her iki sunucuda da olduğundan emin olun.{Style.RESET_ALL}")
        await client.close()
        return

    await Clone.guild_edit(guild_to, guild_from)

    if clone_roles:
        print(f"\n{Fore.CYAN}--- Roller İşleniyor ---{Style.RESET_ALL}")
        await Clone.roles_delete(guild_to)
        await Clone.roles_create(guild_to, guild_from)

    if clone_channels:
        print(f"\n{Fore.CYAN}--- Kanallar ve Kategoriler İşleniyor ---{Style.RESET_ALL}")
        await Clone.channels_delete(guild_to)
        await Clone.categories_create(guild_to, guild_from)
        await Clone.channels_create(guild_to, guild_from)

    if clone_emojis:
        print(f"\n{Fore.CYAN}--- Emojiler İşleniyor ---{Style.RESET_ALL}")
        await Clone.emojis_delete(guild_to)
        await Clone.emojis_create(guild_to, guild_from)

    if clone_stickers:
        print(f"\n{Fore.CYAN}--- Çıkartmalar İşleniyor ---{Style.RESET_ALL}")
        await Clone.stickers_delete(guild_to)
        await Clone.stickers_create(guild_to, guild_from)
    
    print(f"\n{Fore.GREEN}[SUCCESS] Kopyalama İşlemleri Başarıyla Tamamlandı!{Style.RESET_ALL}")
    await asyncio.sleep(3)
    await client.close()

if __name__ == "__main__":
    client.run(token)

# Yusuf Cebeci @58tc
