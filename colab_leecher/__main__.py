# copyright 2024 © Xron Trix | https://github.com/Xrontrix10


import logging
from asyncio import sleep
from pyrogram import filters
from .utility.variables import BOT
from colab_leecher import colab_bot, OWNER
from .utility.task_manager import task_starter
from .utility.helper import is_link_or_path, setThumbnail, message_deleter

# Handler functions
from .handlers import utils
from .handlers.transload import handle_transload
from .handlers.callbacks import handle_callbacks, set_prefix_suffix

src_request_msg = None


# ================= Utility Handlers =================


# /start command handler
@colab_bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await utils.start(message)


# /settings command handler
@colab_bot.on_message(filters.command("settings") & filters.user(OWNER))
async def settings(client, message):
    await message.delete()
    await utils.send_settings(message, message.id, True)


# /help command handler
@colab_bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    await utils.help_command(message)


# =================== Thumbnail Handler =====================


# sets thumbnail image
@colab_bot.on_message(filters.photo & filters.private)
async def handle_image(client, message):
    msg = await message.reply_text(
        "<i>Trying To Save Thumbnail...</i>", parse_mode="HTML"
    )
    success = await setThumbnail(message)
    if success:
        await msg.edit_text(
            "<b>Thumbnail Successfully Changed ✅</b>", parse_mode="HTML"
        )
        await message.delete()
    else:
        await msg.edit_text(
            "🥲 <b>Couldn't Set Thumbnail, Please Try Again !</b>",
            quote=True,
            parse_mode="HTML",
        )
    await sleep(15)
    await message_deleter(message, msg)


# ================== Leech Utility Handlers =================


# /setname command handler
@colab_bot.on_message(filters.command("setname") & filters.private)
async def custom_name(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/setname <code>custom_fileame.extension</code>\nTo Set Custom File Name 📛",
            quote=True,
        )
    else:
        BOT.Options.custom_name = message.command[1]
        msg = await message.reply_text(
            "Custom Name Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


# /zipaswd command handler
@colab_bot.on_message(filters.command("zipaswd") & filters.private)
async def zip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/zipaswd <code>password</code>\nTo Set Password for Output Zip File. 🔐",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text(
            "Zip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


# /unzipaswd command handler
@colab_bot.on_message(filters.command("unzipaswd") & filters.private)
async def unzip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/unzipaswd <code>password</code>\nTo Set Password for Extracting Archives. 🔓",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text(
            "Unzip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


# ================== Callback Handlers =================


@colab_bot.on_callback_query()
async def handle_options(client, callback_query):
    await handle_callbacks(callback_query)


@colab_bot.on_message(filters.reply)
async def setPrefix(client, message):
    await set_prefix_suffix(message)


# ================== Transload Handlers =================


@colab_bot.on_message(filters.command("tupload") & filters.private)
async def telegram_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("gdupload") & filters.private)
async def drive_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("drupload") & filters.private)
async def directory_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me FOLDER PATH 🔗»</b>\n\n🦀 Below is an example\n\n<code>/home/user/Downloads/bot</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("ytupload") & filters.private)
async def yt_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True

    text = "<b>⚡ Send YTDL DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.create(is_link_or_path) & ~filters.photo)
async def handle_url(client, message):

    src_request_msg and await src_request_msg.delete()
    await handle_transload(message)


logging.info("Colab Leecher Started !")
colab_bot.run()
