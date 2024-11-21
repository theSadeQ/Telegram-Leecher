# copyright 2024 © Xron Trix | https://github.com/XronTrix10

import logging
from asyncio import sleep
from pyrogram.errors import BadRequest
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.variables import BOT, MSG, BotTimes, Paths
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from colab_leecher.utility.helper import message_deleter


async def start(message):
    """
    Handle the /start command for the Colab Leecher bot.

    This function deletes the incoming message and sends a welcome message
    with information about the bot's capabilities. It also includes an
    inline keyboard with buttons linking to the bot's repository and support chat.

    Parameters:
    message (pyrogram.types.Message): The message object that triggered this command.
    """
    text = (
        "**Hey There, 👋🏼 It's Colab Leecher**\n\n"
        "◲ I am a Powerful File Transloading Bot 🚀\n"
        "◲ I can Transfer Files To Telegram or Your Google Drive From Various Sources 🦐"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Repository 🦄",
                    url="https://github.com/XronTrix10/Telegram-Leecher",
                ),
                InlineKeyboardButton("Support 💝", url="https://t.me/Colab_Leecher"),
            ],
        ]
    )
    sent = await message.reply_photo(
        photo="https://user-images.githubusercontent.com/125879861/255391401-371f3a64-732d-4954-ac0f-4f093a6605e1.png",
        caption=text,
        reply_markup=keyboard,
    )
    await sleep(15)
    await message_deleter(message, sent)


async def send_settings(message, msg_id, command: bool):
    """
    Send or edit a message displaying the current bot settings with an inline keyboard.

    This function constructs a message with the current settings of the bot and sends it
    as a reply or edits an existing message based on the `command` flag. It includes an
    inline keyboard for further interaction with options to modify settings.

    Parameters:
    message (pyrogram.types.Message): The message object that triggered this function.
    msg_id (int): The ID of the message to edit if `command` is False.
    command (bool): A flag indicating whether to send a new message (True) or edit an existing one (False).

    Raises:
    BadRequest: If the message text is the same and cannot be modified.
    Exception: For any other errors encountered during message modification.
    """
    up_mode = "document" if BOT.Options.stream_upload else "media"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"Set {up_mode.capitalize()}", callback_data=up_mode
                ),
                InlineKeyboardButton("Video Settings", callback_data="video"),
            ],
            [
                InlineKeyboardButton("Caption Font", callback_data="caption"),
                InlineKeyboardButton("Thumbnail", callback_data="thumb"),
            ],
            [
                InlineKeyboardButton("Set Suffix", callback_data="set-suffix"),
                InlineKeyboardButton("Set Prefix", callback_data="set-prefix"),
            ],
            [InlineKeyboardButton("Close ✘", callback_data="close")],
        ]
    )
    text = "**CURRENT BOT SETTINGS ⚙️ »**"
    text += f"\n\n╭⌬ UPLOAD » <i>{BOT.Setting.stream_upload}</i>"
    text += f"\n├⌬ SPLIT » <i>{BOT.Setting.split_video}</i>"
    text += f"\n├⌬ CONVERT » <i>{BOT.Setting.convert_video}</i>"
    text += f"\n├⌬ CAPTION » <i>{BOT.Setting.caption}</i>"
    pr = "None" if BOT.Setting.prefix == "" else "Exists"
    su = "None" if BOT.Setting.suffix == "" else "Exists"
    thmb = "None" if not BOT.Setting.thumbnail else "Exists"
    text += f"\n├⌬ PREFIX » <i>{pr}</i>\n├⌬ SUFFIX » <i>{su}</i>"
    text += f"\n╰⌬ THUMBNAIL » <i>{thmb}</i>"
    try:
        if command:
            await message.reply_text(text=text, reply_markup=keyboard)
        else:
            await colab_bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=text,
                reply_markup=keyboard,
            )
    except BadRequest as error:
        logging.error(f"Same text not modified | {error}")
    except Exception as error:
        logging.error(f"Error Modifying message | {error}")


async def help_command(message):
    """
    Handle the /help command for the bot.

    This function sends a help message to the user, providing information
    about various commands and features available in the bot. It also includes
    an inline keyboard with buttons linking to instructions, the channel, and the group.

    Parameters:
    message (pyrogram.types.Message): The message object that triggered this command.
    """
    help_text = (
        "Send /start To Check If I am alive 🤨\n\n"
        "Send /colabxr and follow prompts to start transloading 🚀\n\n"
        "Send /settings to edit bot settings ⚙️\n\n"
        "Send /setname To Set Custom File Name 📛\n\n"
        "Send /zipaswd To Set Password For Zip File 🔐\n\n"
        "Send /unzipaswd To Set Password to Extract Archives 🔓\n\n"
        "⚠️ **You can ALWAYS SEND an image To Set it as THUMBNAIL for your files 🌄**"
    )

    msg = await message.reply_text(
        help_text,
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Instructions 📖",
                        url="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Channel 📣",
                        url="https://t.me/Colab_Leecher",
                    ),
                    InlineKeyboardButton(
                        "Group 💬",
                        url="https://t.me/Colab_Leecher_Discuss",
                    ),
                ],
            ]
        ),
    )
    await sleep(15)
    await message_deleter(message, msg)
