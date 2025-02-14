import logging
import os
from pyrogram import filters
from datetime import datetime
from asyncio import sleep, get_event_loop
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.handler import cancelTask
from .utility.variables import BOT, MSG, BotTimes, Paths
from .utility.task_manager import taskScheduler, task_starter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utility.helper import isLink, setThumbnail, message_deleter, send_settings

src_request_msg = None

async def send_task_message(message):
    text = "#STARTING_TASK\n\n**Task kicking off soon... just hang tight 🦐🔥**"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]])
    return await colab_bot.send_message(
        chat_id=OWNER,
        text=text,
        reply_markup=keyboard,
    )


async def send_file_links_request(message, mode):
    text = "<b>⚡ Yo, Send Me THEM LINK(s) 🔗»</b>\n\n🦀 Ayo, follow the flow, Let’s get them files pronto, let’s go!\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mkv\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"
    global src_request_msg
    src_request_msg = await task_starter(message, text)
    BOT.Mode.mode = mode
    BOT.Mode.ytdl = False


async def send_directory_request(message):
    text = "<b>⚡ Yo, Send Me THAT FOLDER PATH 🔗»</b>🦀 Check the example below, and let’s get it rollin’!<code>/home/user/Downloads/bot 🚀</code>"
    global src_request_msg
    src_request_msg = await task_starter(message, text)
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False


async def start_handler(client, message):
    await message.delete()
    text = "**Yo! 👋🏼 It's Colab Leecher**\n\n◲ the illest bot to move files to Telegram or Google Drive 🚀\n◲ fast and clean—let me do the dirty work! 🦐"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Repository 📦", url="https://github.com/thesadeq/Telegram-Leecher"),
                InlineKeyboardButton("In SadeQ We 💝", url="https://realmadrid.com"),
            ],
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)


@colab_bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await start_handler(client, message)


@colab_bot.on_message(filters.command("tupload") & filters.private)
async def telegram_upload(client, message):
    await send_file_links_request(message, "leech")


@colab_bot.on_message(filters.command("gdupload") & filters.private)
async def drive_upload(client, message):
    await send_file_links_request(message, "mirror")


@colab_bot.on_message(filters.command("drupload") & filters.private)
async def directory_upload(client, message):
    await send_directory_request(message)


@colab_bot.on_message(filters.command("ytupload") & filters.private)
async def yt_upload(client, message):
    await send_file_links_request(message, "leech")
    BOT.Mode.ytdl = True


@colab_bot.on_message(filters.command("settings") & filters.private)
async def settings(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


@colab_bot.on_message(filters.reply)
async def setPrefix(client, message):
    global BOT
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()


@colab_bot.on_message(filters.create(isLink) & ~filters.photo)
async def handle_url(client, message):
    global BOT

    # Reset
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""

    if src_request_msg:
        await src_request_msg.delete()
    if BOT.State.task_going == False and BOT.State.started:
        temp_source = message.text.splitlines()

        # Check for arguments in message
        for _ in range(3):
            if temp_source[-1][0] == "[":  # Custom name
                BOT.Options.custom_name = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "{":  # Zip password
                BOT.Options.zip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "(":  # Unzip password
                BOT.Options.unzip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            else:
                break

        BOT.SOURCE = temp_source
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Regular", callback_data="normal")],
                [
                    InlineKeyboardButton("Compress 🧳", callback_data="zip"),
                    InlineKeyboardButton("Extract 🔓", callback_data="unzip"),
                ],
                [InlineKeyboardButton("UnDoubleZip 🚨", callback_data="undzip")],
            ]
        )
        await message.reply_text(
            text=f"<b>🐹 Select Type of {BOT.Mode.mode.capitalize()} You Want » </b>\n\nRegular:<i> Normal file upload</i>\nCompress:<i> Zip file upload</i>\nExtract:<i> extract before upload</i>\nUnDoubleZip:<i> Unzip then compress</i>",
            reply_markup=keyboard,
            quote=True,
        )
    elif BOT.State.started:
        await message.delete()
        await message.reply_text(
            "<i>🚨 I'm already grindin'! Hold tight 'til I'm done 😣💪!</i>"
        )


@colab_bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    msg = await message.reply_text(
        "Send /start To Check If I am alive 🤨\n\nSend /colabxr and follow prompts to start transloading 🚀\n\nSend /settings to edit bot settings ⚙️\n\nSend /setname To Set Custom File Name 📛\n\nSend /zipaswd To Set Password For Zip File 🔐\n\nSend /unzipaswd To Set Password to Extract Archives 🔓\n\n⚠️ **You can ALWAYS SEND an image To Set it as THUMBNAIL for your files 🌄**",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Instructions 📖", url="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS")],
                [
                    InlineKeyboardButton("Main Channel 📣", url="https://t.me/Colab_Leecher"),
                    InlineKeyboardButton("Repo's Group 💬", url="https://t.me/Colab_Leecher_Discuss"),
                ],
            ]
        ),
    )
    await sleep(15)
    await message_deleter(message, msg)


logging.info("Colab Leecher Started 🟢!")
colab_bot.run()
