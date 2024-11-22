# copyright 2024 © Xron Trix | https://github.com/XronTrix10

import os
from pyrogram import enums
from datetime import datetime
from asyncio import get_event_loop
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.handler import cancelTask
from colab_leecher.utility.task_manager import taskScheduler
from colab_leecher.utility.variables import BOT, MSG, BotTimes, Paths, captions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# handler fuctions
from colab_leecher.handlers import utils


async def handle_callbacks(callback_query: CallbackQuery):
    global BOT, MSG

    # ========== ENTRY POINT ==========
    if callback_query.data in ["normal", "zip", "unzip", "undzip"]:
        # @main Triggering Actual Leech Functions
        await set_leech_Type(callback_query)

    elif callback_query.data == "video":
        await handle_video_settings(callback_query)

    elif callback_query.data == "caption":
        await caption_styles(callback_query)

    elif callback_query.data.startswith("font-"):
        await set_caption_style(callback_query)

    elif callback_query.data == "thumb":
        await manage_thumbnail(callback_query)

    elif callback_query.data == "del-thumb":
        await delete_thumbnail(callback_query)

    elif callback_query.data in ["set-prefix", "set-suffix"]:
        await prefix_suffix_setter(callback_query)

    elif callback_query.data in ["split-true", "split-false"]:
        await video_split_option(callback_query)

    elif callback_query.data in ["convert-true", "convert-false"]:
        await video_convert_options(callback_query)

    elif callback_query.data in ["q-High", "q-Low"]:
        await video_quality_options(callback_query)

    elif callback_query.data in ["mp4", "mkv"]:
        await video_format_options(callback_query)
    
    elif callback_query.data in ["media", "document"]:
        await stream_upload_options(callback_query)

    elif callback_query.data == "close":
        await callback_query.message.delete()

    elif callback_query.data == "back":
        await utils.send_settings(callback_query.message, callback_query.message.id, False)

    # If user Wants to Stop The Task
    elif callback_query.data == "cancel":
        await cancelTask("User Cancelled !")



# ================== Auxilary Callback Handlers =================


async def set_leech_Type(callback_query: CallbackQuery):
    global BOT

    BOT.Mode.type = callback_query.data
    await callback_query.message.delete()
    await colab_bot.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=callback_query.message.reply_to_message_id,
    )

    # Send a Reaction to the user
    await colab_bot.send_chat_action(chat_id=OWNER, action=enums.ChatAction.TYPING)

    BOT.State.task_going = True
    BOT.State.started = False
    BotTimes.start_time = datetime.now()
    event_loop = get_event_loop()
    BOT.TASK = event_loop.create_task(taskScheduler())  # type: ignore
    await BOT.TASK
    BOT.State.task_going = False


async def handle_video_settings(callback_query: CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Split Videos", callback_data="split-true"),
                InlineKeyboardButton("Zip Videos", callback_data="split-false"),
            ],
            [
                InlineKeyboardButton("Convert", callback_data="convert-true"),
                InlineKeyboardButton("Don't Convert", callback_data="convert-false"),
            ],
            [
                InlineKeyboardButton("To » Mp4", callback_data="mp4"),
                InlineKeyboardButton("To » Mkv", callback_data="mkv"),
            ],
            [
                InlineKeyboardButton("High Quality", callback_data="q-High"),
                InlineKeyboardButton("Low Quality", callback_data="q-Low"),
            ],
            [InlineKeyboardButton("Back ⏎", callback_data="back")],
        ]
    )

    text = (
        "CHOOSE YOUR DESIRED OPTION ⚙️ »\n\n"
        f"╭⌬ CONVERT » <code>{BOT.Setting.convert_video}</code>\n"
        f"├⌬ SPLIT » <code>{BOT.Setting.split_video}</code>\n"
        f"├⌬ OUTPUT FORMAT » <code>{BOT.Options.video_out}</code>\n"
        f"╰⌬ OUTPUT QUALITY » <code>{BOT.Setting.convert_quality}</code>"
    )

    await callback_query.message.edit_text(text, reply_markup=keyboard)


async def caption_styles(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Monospace", callback_data="font-Monospace"),
                InlineKeyboardButton("Bold", callback_data="font-Bold"),
            ],
            [
                InlineKeyboardButton("Italic", callback_data="font-Italic"),
                InlineKeyboardButton("Underlined", callback_data="font-Underlined"),
            ],
            [
                InlineKeyboardButton("Regular", callback_data="font-Regular"),
                InlineKeyboardButton("Quote", callback_data="font-Quote"),
            ],
        ]
    )

    text = (
        "CHOOSE YOUR CAPTION FONT STYLE »\n\n"
        "⌬ <code>Monospace</code>\n"
        "⌬ Regular\n"
        "⌬ <b>Bold</b>\n"
        "⌬ <i>Italic</i>\n"
        "⌬ <u>Underlined</u>\n"
        "⌬ <blockquote>Quote</blockquote>"
    )

    await callback_query.message.edit_text(text=text, reply_markup=keyboard)


async def set_caption_style(callback_query: CallbackQuery):
    global BOT

    res = callback_query.data.split("-")
    BOT.Options.caption = captions[res[0]]
    BOT.Setting.caption = res[1]
    await utils.send_settings(callback_query.message, callback_query.message.id, False)
    await callback_query.answer(
        f"✅ Caption style changed to » <{captions[res[0]]}>{res[1]}</{captions[res[0]]}>",
        show_alert=True,
    )


async def manage_thumbnail(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Delete Thumbnail", callback_data="del-thumb"),
            ],
            [
                InlineKeyboardButton("Go Back ⏎", callback_data="back"),
            ],
        ]
    )
    thmb_ = "None" if not BOT.Setting.thumbnail else "Exists"
    text = (
        f"CHOOSE YOUR THUMBNAIL SETTINGS »\n\n⌬ Thumbnail » {thmb_}\n"
        "⌬ Send an Image to set as Your Thumbnail"
    )
    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


async def delete_thumbnail(callback_query: CallbackQuery):
    global BOT

    if BOT.Setting.thumbnail:
        os.remove(Paths.THMB_PATH)
    BOT.Setting.thumbnail = False
    await utils.send_settings(callback_query.message, callback_query.message.id, False)


async def prefix_suffix_setter(callback_query: CallbackQuery):
    global BOT

    if callback_query.data == "set-prefix":
        await callback_query.message.edit_text(
            "Send a Text to Set as PREFIX by REPLYING THIS MESSAGE »"
        )
        BOT.State.prefix = True
    elif callback_query.data == "set-suffix":
        await callback_query.message.edit_text(
            "Send a Text to Set as SUFFIX by REPLYING THIS MESSAGE »"
        )
        BOT.State.suffix = True


async def set_prefix_suffix(message):
    global BOT

    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False

        await utils.send_settings(message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False

        await utils.send_settings(message, message.reply_to_message_id, False)
        await message.delete()


async def video_split_option(callback_query: CallbackQuery):
    global BOT

    BOT.Options.is_split = True if callback_query.data == "split-true" else False
    BOT.Setting.split_video = (
        "Split Videos" if callback_query.data == "split-true" else "Zip Videos"
    )
    await utils.send_settings(callback_query.message, callback_query.message.id, False)


async def video_convert_options(callback_query: CallbackQuery):
    global BOT

    BOT.Options.convert_video = (
        True if callback_query.data == "convert-true" else False
    )
    BOT.Setting.convert_video = (
        "Yes" if callback_query.data == "convert-true" else "No"
    )
    await callback_query.answer(
        f"✅ Videos will {"" if BOT.Options.convert_video else "not"} be converted to MP4/MKV",
        show_alert=True,
    )
    await utils.send_settings(callback_query.message, callback_query.message.id, False)


async def video_quality_options(callback_query: CallbackQuery):
    global BOT

    BOT.Setting.convert_quality = callback_query.data.split("-")[-1]
    BOT.Options.convert_quality = (
        True if BOT.Setting.convert_quality == "High" else False
    )
    await callback_query.answer(
        f"✅ Videos will be converted to {BOT.Setting.convert_quality} Quality",
        show_alert=True,
    )
    await utils.send_settings(callback_query.message, callback_query.message.id, False)


async def video_format_options(callback_query: CallbackQuery):
    global BOT

    BOT.Options.video_out = callback_query.data
    await callback_query.answer(
        f"✅ Videos will be converted to {BOT.Options.video_out} format",
        show_alert=True,
    )
    await utils.send_settings(callback_query.message, callback_query.message.id, False)


async def stream_upload_options(callback_query: CallbackQuery):
    global BOT

    BOT.Options.stream_upload = True if callback_query.data == "media" else False
    BOT.Setting.stream_upload = (
            "Media" if callback_query.data == "media" else "Document"
        )
    await callback_query.answer(
        f"✅ Files will be uploaded as {BOT.Setting.stream_upload}",
        show_alert=True,
    )
    await utils.send_settings(
            callback_query.message, callback_query.message.id, False
        )