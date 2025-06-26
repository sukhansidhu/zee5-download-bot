import os
import requests
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a Zee5 link and I'll try to fetch the video!")

def extract_id_from_url(url):
    return url.strip("/").split("/")[-1]

def get_zee5_video_info(url):
    try:
        content_id = extract_id_from_url(url)
        details_url = f"https://gwapi.zee5.com/content/details/{content_id}?translation=en&country=IN&version=2"
        token = requests.get("https://useraction.zee5.com/token/platform_tokens.php?platform_name=web_app").json().get("token")
        video_token = requests.get("http://useraction.zee5.com/tokennd/").json().get("video_token")
        headers = {"x-access-token": token}
        data = requests.get(details_url, headers=headers).json()
        if data.get("error_code") == 101 or not data.get("hls"):
            return None, "DRM-protected or invalid content."

        hls = data["hls"][0].replace("drm", "hls")
        final_url = f"https://zee5vodnd.akamaized.net{hls}{video_token}"
        return {
            "title": data.get("title", "Zee5Video"),
            "video_url": final_url
        }, None
    except:
        return None, "Failed to fetch Zee5 info."

def download_video(m3u8_url, output_path):
    cmd = ["ffmpeg", "-i", m3u8_url, "-c", "copy", "-bsf:a", "aac_adtstoasc", output_path]
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("Fetching video info...")
    info, error = get_zee5_video_info(url)
    if error:
        await update.message.reply_text(f"❌ {error}")
        return
    title = info["title"]
    video_url = info["video_url"]
    file_path = f"{title.replace(' ', '_')}.mp4"
    await update.message.reply_text("Downloading video, please wait...")
    if not download_video(video_url, file_path):
        await update.message.reply_text("❌ Failed to download video.")
        return
    await update.message.reply_video(video=open(file_path, "rb"), caption=title)
    os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
