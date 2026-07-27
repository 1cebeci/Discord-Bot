import os
import sys
import datetime
import requests
import keyboard
import winsound

TOKEN = "YOUR_USER_TOKEN"
TARGET_USER_ID = ""
TARGET_CHANNEL_ID = ""
SAVE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "Discord_Exports")
HOTKEY = "alt+s"
DOWNLOAD_MEDIA = True
FILTER_ONLY_USER = False
LIMIT = 100

def get_headers():
    return {
        "Authorization": TOKEN.strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def get_dm_channel_id(user_id):
    r = requests.get("https://discord.com/api/v9/users/@me/channels", headers=get_headers())
    if r.status_code == 200:
        for ch in r.json():
            if ch.get("type") == 1:
                recipients = ch.get("recipients", [])
                if any(u.get("id") == str(user_id) for u in recipients):
                    return ch.get("id")
    return None

def fetch_messages(channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={LIMIT}"
    r = requests.get(url, headers=get_headers())
    if r.status_code == 200:
        return r.json()
    return []

def download_media_file(url, folder, filename):
    try:
        r = requests.get(url, headers=get_headers(), stream=True)
        if r.status_code == 200:
            path = os.path.join(folder, filename)
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return path
    except Exception:
        pass
    return None

def export_job():
    if not TOKEN or TOKEN == "YOUR_USER_TOKEN":
        winsound.Beep(400, 300)
        return

    channel_id = TARGET_CHANNEL_ID
    if not channel_id and TARGET_USER_ID:
        channel_id = get_dm_channel_id(TARGET_USER_ID)

    if not channel_id:
        winsound.Beep(400, 300)
        return

    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    media_dir = os.path.join(SAVE_PATH, "media")
    if DOWNLOAD_MEDIA and not os.path.exists(media_dir):
        os.makedirs(media_dir)

    messages = fetch_messages(channel_id)
    if not messages:
        winsound.Beep(500, 400)
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(SAVE_PATH, f"log_{channel_id}_{timestamp}.txt")

    lines = []
    for msg in reversed(messages):
        author = msg.get("author", {})
        author_id = str(author.get("id", ""))

        if FILTER_ONLY_USER and TARGET_USER_ID and author_id != str(TARGET_USER_ID):
            continue

        name = author.get("global_name") or author.get("username", "Unknown")
        time_str = msg.get("timestamp", "")[:19].replace("T", " ")
        content = msg.get("content", "")

        lines.append(f"[{time_str}] {name} ({author_id}): {content}")

        attachments = msg.get("attachments", [])
        for att in attachments:
            url = att.get("url")
            fname = att.get("filename", "file")
            is_voice = "voice-message" in att.get("flags", 0) or fname.endswith((".ogg", ".mp3", ".wav"))
            tag = "[SES MESAJI]" if is_voice else "[MEDYA/DOSYA]"
            lines.append(f"  {tag} {fname} -> {url}")

            if DOWNLOAD_MEDIA and url:
                save_name = f"{msg.get('id')}_{fname}"
                download_media_file(url, media_dir, save_name)

    if lines:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        winsound.Beep(1200, 150)
        print(f"Saved: {out_file}")

if __name__ == "__main__":
    keyboard.add_hotkey(HOTKEY, export_job)
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass
