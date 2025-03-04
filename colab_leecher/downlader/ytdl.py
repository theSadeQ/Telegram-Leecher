import logging
import yt_dlp
from asyncio import sleep
from threading import Thread
from os import makedirs, path as ospath
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# Assuming you have these variables defined:
# from colab_leecher.utility.variables import YTDL, MSG, Messages, Paths
# from colab_leecher.utility.helper import getTime, keyboard, sizeUnit, status_bar, sysINFO
# from colab_leecher.utility.handler import cancelTask

# Example placeholders, replace with your actual variables
class YTDL:
    header = ""
    speed = "N/A"
    percentage = 0.0
    eta = "N/A"
    done = "N/A"
    left = "N/A"

class MSG:
    status_msg = None

class Messages:
    status_head = ""
    task_msg = ""

class Paths:
    thumbnail_ytdl = "thumbnails"
    down_path = "downloads"

# Example placeholders for helper functions, replace with your actual functions
def getTime(seconds):
    return f"{seconds}s"

def sizeUnit(bytes):
    return f"{bytes} bytes"

async def status_bar(down_msg, speed, percentage, eta, done, left, engine):
    if MSG.status_msg:
        await MSG.status_msg.edit_text(f"{down_msg}\nSpeed: {speed}, {percentage}%, ETA: {eta}, Done: {done}, Left: {left}, Engine: {engine}")

def sysINFO():
    return ""

async def cancelTask(message):
    print(f"Task cancelled: {message}")

download_number = 0  # Global to keep track of download numbers

async def YTDL_Status(link, quality="best"):
    global Messages, YTDL, download_number
    download_number += 1
    num = download_number
    name = await get_YT_Name(link)
    Messages.status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n<code>{name}</code>\n"

    YTDL_Thread = Thread(target=YouTubeDL, name="YouTubeDL", args=(link, quality))
    YTDL_Thread.start()

    while YTDL_Thread.is_alive():
        if YTDL.header:
            sys_text = sysINFO()
            message = YTDL.header
            try:
                if MSG.status_msg:
                    await MSG.status_msg.edit_text(text=Messages.task_msg + Messages.status_head + message + sys_text)
            except Exception as e:
                logging.error(f"Error editing message: {e}")
        else:
            try:
                await status_bar(
                    down_msg=Messages.status_head,
                    speed=YTDL.speed,
                    percentage=float(YTDL.percentage),
                    eta=YTDL.eta,
                    done=YTDL.done,
                    left=YTDL.left,
                    engine="Xr-YtDL 🏮",
                )
            except Exception as e:
                logging.error(f"Error updating status: {e}")

        await sleep(2.5)

class MyLogger:
    def __init__(self):
        pass

    def debug(self, msg):
        global YTDL
        if "item" in str(msg):
            msgs = msg.split(" ")
            YTDL.header = f"\n⏳ __Getting Video Information {msgs[-3]} of {msgs[-1]}__"

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def error(msg):
        pass

def YouTubeDL(url, quality="best"):
    global YTDL

    def my_hook(d):
        global YTDL

        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes", 0)
            dl_bytes = d.get("downloaded_bytes", 0)
            percent = d.get("downloaded_percent", 0)
            speed = d.get("speed", "N/A")
            eta = d.get("eta", 0)

            if total_bytes:
                percent = round((float(dl_bytes) * 100 / float(total_bytes)), 2)

            YTDL.header = ""
            YTDL.speed = sizeUnit(speed) if speed else "N/A"
            YTDL.percentage = percent
            YTDL.eta = getTime(eta) if eta else "N/A"
            YTDL.done = sizeUnit(dl_bytes) if dl_bytes else "N/A"
            YTDL.left = sizeUnit(total_bytes) if total_bytes else "N/A"

        elif d["status"] == "downloading fragment":
            pass
        else:
            logging.info(d)

    if quality == "best":
        format_string = "bestvideo+bestaudio/best"
    elif quality == "720p":
        format_string = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif quality == "1080p":
        format_string = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    elif quality == "480p":
        format_string = "bestvideo[height<=480]+bestaudio/best[height<=480]"
    else:
        format_string = "bestvideo+bestaudio/best"

    ydl_opts = {
        "format": format_string,
        "allow_multiple_video_streams": True,
        "allow_multiple_audio_streams": True,
        "writethumbnail": True,
        "--concurrent-fragments": 4,
        "allow_playlist_files": True,
        "overwrites": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "progress_hooks": [my_hook],
        "writesubtitles": "srt",
        "extractor_args": {"subtitlesformat": "srt"},
        "logger": MyLogger(),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not ospath.exists(Paths.thumbnail_ytdl):
            makedirs(Paths.thumbnail_ytdl)
        try:
            info_dict = ydl.extract_info(url, download=False)
            YTDL.header = "⌛ __Please WAIT a bit...__"
            if "_type" in info_dict and info_dict["_type"] == "playlist":
                playlist_name = info_dict["title"]
                if not ospath.exists(ospath.join(Paths.down_path, playlist_name)):
                    makedirs(ospath.join(Paths.down_path, playlist_name))
                ydl_opts["outtmpl"] = {
                    "default": f"{Paths.down_path}/{playlist_name}/%(title)s.%(ext)s",
                    "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                }
                for entry in info_dict["entries"]:
                    video_url = entry["webpage_url"]
                    try:
                        ydl.download([video_url])
                    except yt_dlp.utils.DownloadError as e:
                        if e.exc_info[0] == 36:
                            ydl_opts["outtmpl"] = {
                                "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                                "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                            }
                            ydl.download([video_url])
            else:
                YTDL.header = ""
                ydl_opts["outtmpl"] = {
                    "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                    "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                }
                try:
                    ydl.download([url])
                except yt_dlp.utils.DownloadError as e:
                    if e.exc_info[0] == 36:
                        ydl_opts["outtmpl"] = {
                            "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                            "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.
