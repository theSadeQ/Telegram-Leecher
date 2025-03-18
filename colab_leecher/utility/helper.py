import re
import os
import time
import psutil
import shutil
from colab_leecher.utility import variables as var
from moviepy.editor import VideoFileClip
from PIL import Image
from natsort import natsorted
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

#——Checking URL Types——
def isLink(message: Message):
    regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
    if re.match(regex, message):
        return True
    else:
        return False

def is_google_drive(url):
    return "drive.google.com" in url or "docs.google.com" in url

def is_mega(url):
    return "mega.nz" in url or "mega.co.nz" in url

def is_terabox(url):
    return "terabox" in url

def is_ytdl_link(url):
    return "youtube.com" in url or "youtu.be" in url or "vimeo" in url \
           or "facebook.com" in url or "fb.watch" in url or "dailymotion.com" in url

def is_telegram(url):
    return "t.me" in url

def is_torrent(url):
    return url.endswith(".torrent")

#——Calculating Time, Size, Percentage——
def getTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]

def sizeUnit(size):
    B = 1024
    KB = B * 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024
    if size >= TB:
        size = str(round(size / TB, 2)) + ' TB'
    elif size >= GB:
        size = str(round(size / GB, 2)) + ' GB'
    elif size >= MB:
        size = str(round(size / MB, 2)) + ' MB'
    elif size >= KB:
        size = str(round(size / KB, 2)) + ' KB'
    else :
        size = str(round(size, 2)) + ' B'
    return size

def fileType(filename):
    if filename.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')):
        return 'vid'
    elif filename.endswith(('.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a')):
        return 'aud'
    elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
        return 'img'
    else:
        return 'doc'

def shortFileName(filename):
    name, _ = filename.rsplit(".", 1)
    shorted_name = name[:15] + "..." + name[-5:] + "." + _
    return shorted_name

def getSize(directory):
    size = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        size += os.path.getsize(filepath)
    return size

def videoExtFix(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith((".mkv", ".webm", ".avi")):
            _ , ext = filename.rsplit(".", 1)
            new_filepath = filepath.replace("." + ext, ".mp4")
            os.rename(filepath, new_filepath)
            filepath = new_filepath
        thumbMaintainer(filepath) # generate thumbnail

def thumbMaintainer(filepath):
    if fileType(filepath) == "vid":
        try:
            clip = VideoFileClip(filepath)
            duration = int(clip.duration)
            thumbnail = clip.save_frame(var.Paths.THUMB_PATH, t=((duration - 5) if duration > 5 else 0)) # capture thumbnail
            clip.close()
        except Exception as e:
            pass

def setThumbnail(filepath):
    try:
        img = Image.open(filepath)
        img.convert("RGB").save(var.Paths.THUMB_PATH, "JPEG")
    except Exception as e:
        pass

def isYtdlComplete(directory):
    for filename in os.listdir(directory):
        if filename.endswith((".ytdl", ".part")):
            return False
        else:
            return True

def convertIMG(img_path, format="jpg"):
    try:
        img = Image.open(img_path)
        img_rgb = img.convert("RGB")
        file_name, _ = os.path.basename(img_path).rsplit('.', 1)
        new_path = var.BOT_THUMB_DIR + file_name + f'.{format}'
        img_rgb.save(new_path, format)
        img.close()
        os.remove(img_path)
        return new_path
    except Exception as e:
        print(e)
        return img_path

def sysINFO():
    cpu = str(round(psutil.cpu_percent(), 2)) + "%"
    ram = str(round(psutil.virtual_memory().percent, 2)) + "%"
    total, used, free = shutil.disk_usage(var.DOWNLOAD_DIR)
    total = sizeUnit(total)
    used = sizeUnit(used)
    free = sizeUnit(free)
    disk = f"{used} / {total}"

    return f"CPU: {cpu}\nRAM: {ram}\nDisk: {disk}"

def multipartArchive(path):
    size = 0
    parts = natsorted(os.listdir(path))
    size = sum(os.path.getsize(os.path.join(path, file)) for file in parts)
    return size, parts

def isTimeOver(time_stamp):
    time_now = time.time()
    if (time_now - time_stamp) >= 10:
        return True
    else:
        return False
#——Messages——
async def message_deleter(message, sleep_time=1):
  try:
    if sleep_time:
        await asyncio.sleep(sleep_time)
    await message.delete()

  except Exception as e:
    print(e)
    pass

async def send_settings(user_id, query=None, message_id=None):
    buttons = await settings_buttons()
    text = var.Messages.SETTINGS
    try:
        if query == "close":
           return await colab_bot.edit_message_reply_markup(user_id, message_id)
        elif query == "refresh":
            return await colab_bot.edit_message_text(user_id, message_id, text=text, reply_markup=buttons, disable_web_page_preview=True)
        else:
            return await colab_bot.send_message(user_id, text, reply_markup=buttons, disable_web_page_preview=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except Exception as e:
        LOG.error(e)
        pass

async def start_buttons():
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="⚙️ Settings", callback_data="setting_set"),
                InlineKeyboardButton(text="Close ❌", callback_data="setting_close")
            ],
        ]
    )
    return markup

async def settings_buttons():
    buttons = [
        [
            InlineKeyboardButton(text=("✅ Enabled" if var.BOT.USE_THUMB else "❌ Disabled"), callback_data="setting_thumb"),
            InlineKeyboardButton(text="🖼️ Custom Thumbnail", callback_data="setting_cthumb")
