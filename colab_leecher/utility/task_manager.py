# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import asyncio
import os
import logging
from colab_leecher.downlader import (
    gdrive,
    mega,
    telegram,
    ytdl,
    nzbcloud,
    deltaleech,
    bitso
)

from colab_leecher.utility.handler import Leech, Unzip_Handler, Zip_Handler, SendLogs, cancelTask
from colab_leecher.utility.helper import is_google_drive, is_mega, is_telegram, is_valid_url, is_magnet, is_ytdl
from colab_leecher.utility.variables import (
    BOT,
    MSG,
    BotTimes,
    Messages,
    Paths,
    Transfer
)
from colab_leecher.utility.helper import is_valid_input_format

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
        link = message.text
        if is_google_drive(link):
            downloader_type = "gdrive"
        elif is_mega(link):
            downloader_type = "mega"
        elif is_telegram(link):
            downloader_type = "telegram"
        elif is_ytdl(link):
            downloader_type = "ytdl"
        elif is_valid_url(link) or is_magnet(link):
            downloader_type = "direct"
        else:
            await message.reply_text("Invalid link provided. 🚫")
            return

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
            if BOT.LEECH.IS_SPLIT:
              await Leech(Paths.temp_zpath, True)  # Leech Split Zip
            else:
              await Leech(Paths.temp_zpath, remove) # leech single zip
        elif is_leech:
            if not BOT.Options.rclone_upload:
              await Leech(Paths.DOWNLOAD_PATH, remove)
        if BOT.Options.rclone_upload: # Rclone
            rc = await rclone_upload()
            if rc == False: # rclone Failed
                if BOT.Mode.compress:
                   await Leech(Paths.temp_zpath, True)
                elif BOT.Mode.extract:
                   await Leech(Paths.temp_unzip_path, True)
                else:
                    await Leech(Paths.DOWNLOAD_PATH, True)
    await SendLogs(is_leech)


async def taskScheduler(client, message):
    global BOT, MSG, BotTimes, Messages, Paths, Transfer
    if message.text == "/cancel":
        if BOT.State.task_going:
            await cancelTask("Cancelled by User")
        else:
            await message.reply_text(text="No task to cancel. 🤷")
        return
    if BOT.State.task_going:
        await message.reply_text(
            text=f"A task is already in progress. Please wait. ⏳\n\n<b>Details:</b>\n• __File:__ `{Messages.download_name}`\n• __Mode:__ `{BOT.Mode.mode}`\n\nUse /cancel to stop current task."
        )
        return

    BotTimes.start_time = message.date
    BOT.State.task_going = True

    # --- Prepare Directories ---
    if not os.path.exists(Paths.DOWNLOAD_PATH):
        os.makedirs(Paths.DOWNLOAD_PATH)
    if not os.path.exists(Paths.UPLOADS_PATH):
        os.makedirs(Paths.UPLOADS_PATH)

    # --- Initial Message to User ---
    sent_message = await message.reply_text(
        text=f"Processing your request... Please wait. ⏳", quote=True
    )
    MSG.sent_msg = sent_message  # Store for later updates

    # --- Determine Leech/Upload Mode ---
    is_leech = False
    if message.text.startswith(("/urlleech", "/gdupload", "/ttupleech")):
        is_leech = True

    # --- URL Template Logic ---
    if message.text.startswith("url_template:"):
        BOT.State.waiting_for_input = False  # No longer waiting
        lines = message.text.splitlines()
        # Extract url_template, segments, filenames
        try:
            url_template = lines[0].split(":", 1)[1].strip()
            variable_segments_line = lines[1].split(":", 1)[1].strip()
            variable_segments = [seg.strip() for seg in variable_segments_line.split(",")]

            try:
                filenames_line = lines[2].split(":", 1)[1].strip()
                filenames = [fname.strip() for fname in filenames_line.split(",")]
            except:
                filenames = None # No filenames given

            referer = None # Add this line
            try: #check if user gives referer
                referer_line = lines[3].split(":", 1)[1].strip()
                referer = referer_line
            except:
                pass
            # Check for custom filenames in square brackets
            if filenames: # Check user inputs filenames or not
                for i, fname in enumerate(filenames):
                    if fname.startswith('[') and fname.endswith(']'):
                        filenames[i] = fname[1:-1]  # Remove brackets

            BOT.Mode.mode = "Leech" if is_leech else "Upload"
            Messages.download_name = filenames[0] if filenames else "Multiple Files"
            Messages.src_link = url_template

            # Call downloadManager with URL template information
            await downloadManager(
                client,
                sent_message,
                message,
                is_leech,
                url_template,
                variable_segments,
                filenames,
                referer
            )

        except Exception as e:
            await message.reply_text(f"Error processing input: {e} ❌")
            BOT.State.task_going = False
            return

    else:
        # --- Regular Download/Leech (No Template) ---
        BOT.State.waiting_for_input = False  # No longer waiting for input
        Messages.download_name = (
            message.text.split("/")[-1]
            if is_leech
            else os.path.basename(message.text)
        )
        Messages.src_link = message.text
        BOT.Mode.mode = "Leech" if is_leech else "Upload"

        await downloadManager(client, sent_message, message, is_leech)


async def task_starter(client, message):
    global BOT, MSG, BotTimes, Messages, Paths, Transfer

    if BOT.State.task_going:
        await message.reply_text(
            text=f"A task is already in progress. Please wait. ⏳\n\n<b>Details:</b>\n• __File:__ `{Messages.download_name}`\n• __Mode:__ `{BOT.Mode.mode}`\n\nUse /cancel to stop the current task."
        )
    elif message.text.startswith(("/urlleech", "/gdupload", "/tupload")):
        BOT.State.waiting_for_input = True
        await message.reply_text(
            "Send your download details in this format:\n\n"
            "`url_template: URL_TEMPLATE`\n"
            "`segments: SEGMENT1,SEGMENT2,...`\n"
            "`filenames: FILE1,FILE2,...` (optional)\n"
            "`cf_clearance: YOUR_CF_CLEARANCE_COOKIE` (optional)\n"
            "`referer: REFERER_URL` (optional)\n\n"
             "Or send a single direct download/magnet/telegram link."
            , quote=True
        )
    else:
        await taskScheduler(client, message)


async def rclone_upload():
    if BOT.RCLONE.enabled:
        from colab_leecher.remote.rclone
