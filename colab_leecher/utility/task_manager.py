from colab_leecher.utility import variables as var
from colab_leecher.utility import helper
from colab_leecher.utility.handler import Do_Leech, Do_Mirror, Zip_Handler, Unzip_Handler
from colab_leecher.utility.converters import splitArchive
from colab_leecher.downlader.manager import downloadManager, get_d_name, calDownSize
from colab_leecher.uploader.telegram import upload_file
from telethon.tl.types import DocumentAttributeFilename
import os
import time
import asyncio
import logging

async def taskScheduler(app, message, unzip=False, leech=False, mssg_id=None):
    try:
        # ... (Rest of the initial setup code from taskScheduler, up to setting BOT_TEMP_DIR) ...
        #——Task Type Varible——
        is_zip = False
        is_unzip = False
        is_leech = False
        is_mirror = False

        #——Message Variables——
        reply_to = None
        file = None
        sent_message = None
        message_text = None
        url_list = []  # Initialize url_list
        download_path = None
        download_name = None
        total_size = None


        #—Task type and Download Path—
        if message.media:
            file = await app.download_media(message, file_name=var.BOT_TEMP_DIR)
            if unzip:
                download_path = var.DOWNLOAD_DIR
                is_unzip = True
            elif leech:
                download_path = var.LEECH_SPLIT_TEMP if var.BOT.AS_SPLIT else var.LEECH_DIR
                is_leech = True
            else:
                download_path = var.BOT_TEMP_DIR
                is_mirror = True

        elif message.text:
            message_text = message.text.strip()
            if mssg_id:
                message_text = message.text.strip()
                global edit_msg
                edit_msg = await app.get_messages(var.BOT.BOT_ID, mssg_id)

            if message_text.startswith("/"):
                return
            #——URL/File Path Recived——
            elif helper.isLink(message_text) or os.path.isfile(message_text):
                if unzip:
                    download_path = var.DOWNLOAD_DIR
                    is_unzip = True
                elif leech:
                    download_path = var.LEECH_SPLIT_TEMP if var.BOT.AS_SPLIT else var.LEECH_DIR
                    is_leech = True
                else:
                    download_path = var.BOT_TEMP_DIR
                    is_mirror = True

                url_list = message_text.split()

            else:
              sent_message = await app.send_message(var.BOT.BOT_ID, var.Messages.INVALID_INPUT, reply_to_message_id=mssg_id)
              return

        if is_unzip:
            if file:
                download_name = file
            else:
            #——Extracting Archive from TG File Link——
                if helper.is_telegram(url_list[0]):
                    sent_message = await app.send_message(var.BOT.BOT_ID, var.Messages.PROCESSING, reply_to_message_id=mssg_id)
                    file = await downloadManager(app, sent_message, message)
                    if not file:
                      await helper.message_deleter(sent_message)
                      return
                    download_name = file
            #——Extracting Archive from URL——
                else:
                    download_name =  var.BOT_TEMP_DIR
                    if len(url_list) > 1:
                        sent_message = await app.send_message(var.BOT.BOT_ID, var.Messages.ONLY_ONE, reply_to_message_id=mssg_id)
                        return
                    sent_message = await app.send_message(var.BOT.BOT_ID, var.Messages.DOWN_BEGUN, reply_to_message_id=mssg_id)
                    await downloadManager(app, sent_message, message, unzip)
            if not download_name:
                return
            await Unzip_Handler(app, sent_message, download_name, mssg_id)
            await helper.message_deleter(sent_message)
            return

        elif is_leech:
            if file:
                download_name = file
            else:
                if helper.is_telegram(url_list[0]):
                    sent_message = await app.send_message(var.BOT.BOT_ID, var.Messages.PROCESSING, reply_to_message_id=mssg_id)
                    file = await downloadManager(app, sent_message, message)
                    if not file:
                      await helper.message_deleter(sent_message)
                      return
                    download_name = file
                else:
                    # Handle URL template for leech
                    if message_text.startswith("url_template:"):
                        try:
                            lines = message_text.splitlines()
                            url_template = lines[0].split(":", 1)[1].strip()
                            segments_line = lines[1].split(":", 1)[1].strip()
                            variable_segments = [seg.strip() for seg in segments_line.split(",")]

                            try: #check if user gives file names
                               filenames_line = lines[2].split(":", 1)[1].strip()
                               filenames = [name.strip() for name in filenames_line.split(",")]
                            except IndexError:
                                filenames = None
                            # Determine downloader type (you'll need to adapt your is_... functions)
                            if helper.is_google_drive(url_template):
                                downloader_type = "gdrive"
                            elif helper.is_mega(url_template):
                                downloader_type = "mega"
                            elif helper.is_terabox(url_template):
                                downloader_type = "terabox"
                            # Add more checks for other downloaders as needed
                            else:
                                downloader_type = "direct"  # Assume direct URL download

                            sent_message
