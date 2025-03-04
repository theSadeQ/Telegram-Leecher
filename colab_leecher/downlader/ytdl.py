# copyright 2023 © Xron Trix | https://github.com/Xrontrix10


import logging
import yt_dlp
from asyncio import sleep
from threading import Thread
from os import makedirs, path as ospath
from colab_leecher.utility.handler import cancelTask
from colab_leecher.utility.variables import YTDL, MSG, Messages, Paths
from colab_leecher.utility.helper import getTime, keyboard, sizeUnit, status_bar, sysINFO


async def YTDL_Status(link, num, quality="best"): # Added quality parameter with default "best"
    global Messages, YTDL
    name = await get_YT_Name(link)
    Messages.status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n<code>{name}</code>\n\n<b>Quality:</b> <code>{quality}</code>\n" # Added quality to status head

    YTDL_Thread = Thread(target=YouTubeDL, name="YouTubeDL", args=(link, quality)) # Passing quality to YouTubeDL
    YTDL_Thread.start()

    while YTDL_Thread.is_alive():  # Until ytdl is downloading
        if YTDL.header:
            sys_text = sysINFO()
            message = YTDL.header
            try:
                await MSG.status_msg.edit_text(text=Messages.task_msg + Messages.status_head + message + sys_text, reply_markup=keyboard())
            except Exception:
                pass
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
            except Exception:
                pass

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
        # if msg != "ERROR: Cancelling...":
        # print(msg)
        pass


def YouTubeDL(url, quality="best"): # Added quality parameter with default "best"
    global YTDL

    def my_hook(d):
        global YTDL

        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes", 0)  # Use 0 as default if total_bytes is None
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
            # log_str = d["message"]
            # print(log_str, end="")
            pass
        else:
            logging.info(d)

    ydl_opts = {
        "format": quality, # Using the quality parameter here
        "allow_multiple_video_streams": True,
        "allow_multiple_audio_streams": True,
        "writethumbnail": True,
        "--concurrent-fragments": 4 , # Set the maximum number of concurrent fragments
        "allow_playlist_files": True,
        "overwrites": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "progress_hooks": [my_hook],
        "writesubtitles": "srt",  # Enable subtitles download
        "extractor_args": {"subtitlesformat": "srt"},  # Extract subtitles in SRT format
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
                            "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                        }
                        ydl.download([url])
        except Exception as e:
            logging.error(f"YTDL ERROR: {e}")


async def get_YT_Name(link):
    with yt_dlp.YoutubeDL({"logger": MyLogger()}) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
            if "title" in info and info["title"]: 
                return info["title"]
            else:
                return "UNKNOWN DOWNLOAD NAME"
        except Exception as e:
            await cancelTask(f"Can't Download from this link. Because: {str(e)}")
            return "UNKNOWN DOWNLOAD NAME"
