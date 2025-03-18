# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import asyncio
import os
import logging
from colab_leecher.utility import variables as var
from colab_leecher.utility import helper
from colab_leecher.utility.handler import Leech, Unzip_Handler, Zip_Handler, SendLogs, cancelTask
from colab_leecher.utility.converters import splitArchive
from colab_leecher.downlader.manager import downloadManager, get_d_name, calDownSize
from colab_leecher.uploader.telegram import upload_file
from telethon.tl.types import DocumentAttributeFilename
import time
from colab_leecher.downlader import (
    gdrive,
    mega,
    telegram,
    ytdl,
    nzbcloud,
    deltaleech,
    bitso # Import bitso
)
from colab_leecher.utility.helper import is_google_drive, is_mega, is_telegram, is_valid_url, is_magnet, is_ytdl, is_bitso
from colab_leecher.utility.variables import (
    BOT,
    MSG,
    BotTimes,
    Messages,
    Paths,
    Transfer
)
from colab_leecher.utility.helper import is_valid_input_format, extract_filename_from_url, clean_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

async def downloadManager(
    app,
    dummy_message,
    message,
    is_leech,
    url_template=None,
    variable_segments=None,
    filenames=None,
    referer=None
):
    global BOT, MSG, BotTimes, Messages, Paths, Transfer

    remove = True if BOT.Options.remove_source else False  # Check for Removal Setting

    # Determine the downloader type based on URL template (if provided) or the message text
    if url_template:
        if is_valid_input_format(url_template, variable_segments, filenames):
            downloader_type = "template"  # Default to template-based
            if "nzbcloud" in url_template.lower():
                downloader_type = "nzbcloud"
            elif "muwi" in url_template.lower() or "delta" in url_template.lower():  # More robust check
                downloader_type = "deltaleech"
        else:
            await message.reply_text("The number of variable segments and filenames do not match. ❌")
            return

    else:  # If no URL template, determine from the message text
        link = message.text.strip()

        if is_google_drive(link):
            downloader_type = "gdrive"
        elif is_mega(link):
            downloader_type = "mega"
        elif is_telegram(link):
            downloader_type = "telegram"
        elif is_ytdl(link):
            downloader_type = "ytdl"
        elif is_bitso(link): # Check for Bitso URL
            downloader_type = "bitso"
        elif is_valid_url(link) or is_magnet(link):
            downloader_type = "direct"
        else:
            await message.reply_text("Invalid link provided. 🚫")
            return
    print(f"Downloader Used: {downloader_type}")
    # Download logic
    match downloader_type:
        case "gdrive":
            logging.info("Downloading from Google Drive...")
            BOT.TASK = await gdrive.g_download(message.text, Paths.DOWNLOAD_PATH)

        case "mega":
            logging.info("Downloading from MEGA...")
            await message.reply_text(
                f"MEGA download started... Please be patient. ⏳\n\n**{Messages.download_name}**"
            )
            BOT.TASK = await mega.mega_download(message.text, Paths.DOWNLOAD_PATH)

        case "telegram":
            logging.info("Downloading from Telegram...")
            BOT.TASK = await telegram.download_telegram_file(app, message, Paths.DOWNLOAD_PATH)

        case "ytdl":
            logging.info("Downloading using yt-dlp...")
            await dummy_message.reply_text(
                f"yt-dlp download started... Please be patient. ⏳\n\n**{Messages.download_name}**"
            )
            BOT.TASK = await ytdl.ytdl_download(message.text, Paths.DOWNLOAD_PATH)

        case "direct":
            logging.info("Direct download started...")
            await dummy_message.reply_text("Direct download is currently not supported. 🚫")
            BOT.State.task_going = False
            return

        case "nzbcloud":
            await dummy_message.reply_text(
                f"nzbCloud download started... Please be patient. ⏳\n\n**{Messages.download_name}**"
            )
            BOT.TASK = asyncio.create_task(
                nzbcloud.download_files_nzbcloud(
                    url_template,
                    variable_segments,
                    filenames,
                    BOT.COOKIES.cf_clearance,
                    Paths.DOWNLOAD_PATH,
                )
            )
            await BOT.TASK

        case "deltaleech":
            await dummy_message.reply_text(
                f"DeltaLeech download started... Please be patient. ⏳\n\n**{Messages.download_name}**"
            )
            BOT.TASK = asyncio.create_task(
                deltaleech.download_multiple_files_deltaleech(
                    url_template,
                    variable_segments,
                    filenames,
                    BOT.COOKIES.cf_clearance,
                    Paths.DOWNLOAD_PATH,
                    referer
                )
            )
            await BOT.TASK

        case "bitso":
            await dummy_message.reply_text(
                f"Bitso download started... Please be patient. ⏳\n\n**{Messages.download_name}**"
            )

            # Bitso requires special handling for cookies and referer, and filenames
            lines = message.text.splitlines()
            urls = []
            filenames = []

            for line in lines:
                line = line.strip()
                if line.startswith("url_template:"):
                    continue #Ignore
                elif line.startswith("segments:"):
                    continue #Ignore
                elif line.startswith("filenames:"):
                    continue #Ignore
                elif line.startswith("cf_clearance:"):
                    continue #Ignore
                elif line.startswith("referer:"):
                    continue #Ignore
                elif line:
                    urls.append(line)

            if filenames is None:
                filenames = []
                if BOT.Options.custom_name:
                  filenames = [f"{BOT.Options.custom_name}_{i + 1}" for i in range(len(urls))]
                else:
                  filenames = [extract_filename_from_url(url) for url in urls]
                # Check if filename extraction was successful
                if any(fname is None for fname in filenames):
                    await dummy_message.reply_text("Could not extract filenames from URLs. Please provide filenames manually. ❌")
                    BOT.State.task_going = False
                    return
            print("--- Bitso Debug ---")
            print(f"URLs: {urls}")
            print(f"Filenames: {filenames}")
            print(f"Referer: {BOT.COOKIES.referer}")
            print(f"_identity: {BOT.COOKIES._identity}")
            print(f"PHPSESSID: {BOT.COOKIES.PHPSESSID}")
            print("--------------------")

            BOT.TASK = asyncio.create_task(
                bitso.download_multiple_files_bitso(
                    urls=urls,  # Pass the list of URLs
                    file_names=filenames,  # Use filenames extracted or provided
                    download_directory=Paths.DOWNLOAD_PATH,
                    referer_url=BOT.COOKIES.referer,  # Pass referer from bot settings
                    _identity_value=BOT.COOKIES._identity,  # Pass _identity
                    phpsessid_value=BOT.COOKIES.PHPSESSID,  # Pass PHPSESSID
                )
            )
            await BOT.TASK

        case _:
            await message.reply_text("Unsupported download type. 🚫")
            BOT.State.task_going = False
            return

    # --- POST-DOWNLOAD ACTIONS ---
    if BOT.State.task_going:  # Only proceed if the download wasn't cancelled.
        # --- Zipping/Unzipping ---
        if BOT.Mode.compress:  # ZIP
            await Zip_Handler(Paths.DOWNLOAD_PATH, BOT.LEECH.IS_SPLIT, remove)  # is_split, remove
            if BOT.LEECH.IS_SPLIT:
              await Leech(Paths.temp_zpath, True)  # Leech Split Zip
            else:
              await Leech(Paths.temp_zpath, remove) # leech single zip
        elif BOT.Mode.extract:  # UNZIP
            await Unzip_Handler(Paths.DOWNLOAD_PATH, remove)
            if not BOT.Options.rclone_upload:
                await Leech(Paths.temp_unzip_path, True)  # Leech Unzipped Files
        elif BOT.Mode.undoublezip:
            await Unzip_Handler(Paths.DOWNLOAD_PATH, remove)
            await Zip_Handler(Paths.temp_unzip_path, BOT.LEECH.IS_SPLIT, True)
            if BOT.LEECH.IS
