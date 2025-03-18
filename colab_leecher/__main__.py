from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import logging
from colab_leecher.utility import variables as var
from colab_leecher.utility import helper
from colab_leecher.utility.task_manager import task_starter
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

# Load credentials from the JSON file
with open('credentials.json', 'r') as f:
    credentials = json.load(f)
API_ID = credentials['API_ID']
API_HASH = credentials['API_HASH']
BOT_TOKEN = credentials['BOT_TOKEN']
USER_ID = credentials['USER_ID']
DUMP_ID = credentials['DUMP_ID']

# Set bot variables
var.BOT.BOT_ID = int(USER_ID)
var.BOT.DUMP_ID = int(DUMP_ID)
var.BOT.BOT_TOKEN = BOT_TOKEN


colab_bot = Client("colab_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=2)


#——Start Message——
async def start_message(client, message):
    buttons = await helper.start_buttons()
    await message.reply(text=var.Messages.START_MSG, reply_markup=buttons, quote=True, disable_web_page_preview=True)

#——Help Message——
async def help_message(client, message):
    await message.reply(text=var.Messages.HELP_MSG, quote=True, disable_web_page_preview=True)

#——Uploading files from Telegram File/Media——
async def upload_from_telegram(client, message):
     await task_starter(colab_bot, message)

#——Uploading files from URL——
async def upload_from_url(client, message):
    await task_starter(colab_bot, message)

#——Uploading files from Google Drive URL——
async def gdrive_upload_from_url(client, message):
    await task_starter(colab_bot, message)

#——Uploading files from Direct URL——
async def direct_upload_from_url(client, message):
    await task_starter(colab_bot, message)

#——Uploading files from yt-dlp supported sites——
async def ytdl_upload_from_url(client, message):
    await task_starter(colab_bot, message, leech=False)

#——Leeching files from Telegram File/Media——
async def leech_from_telegram(client, message):
    await task_starter(colab_bot, message, leech=True)

#——Leeching files from URL——
async def leech_from_url(client, message):
   await task_starter(colab_bot, message, leech=True)

#——Unzipping files——
async def unzip_from_telegram(client, message):
    await task_starter(colab_bot, message, unzip=True)

#——Unzipping files from URL——
async def unzip_from_url(client, message):
    await task_starter(colab_bot, message, unzip=True)

#——Callback Query Handler (Settings)——
async def settings_handler(client, call):
    await helper.send_settings(call.from_user.id, call.data, call.message.id)

async def set_rename_prefix(client, message):
    if  message.text.startswith("/"):
        return
    var.BOT.RENAME_PREFIX = message.text
    await message.reply(var.Messages.NAME_SET, quote=True)

async def set_zip_password(client, message):
    if  message.text.startswith("/"):
        return
    var.BOT.ZIP_PASSWORD = message.text
    await message.reply(var.Messages.ZIP_ASWD_SET, quote=True)

async def set_unzip_password(client, message):
    if  message.text.startswith("/"):
        return
    var.BOT.UNZIP_PASSWORD = message.text
    await message.reply(var.Messages.UNZIP_ASWD_SET, quote=True)


#——Handlers——
colab_bot.add_handler(MessageHandler(start_message, filters.command(["start"]) & filters.private))

colab_bot.add_handler(MessageHandler(help_message, filters.command(["help"]) & filters.private))

colab_bot.add_handler(MessageHandler(ytdl_upload_from_url, filters.command(["ytupload"]) & filters.private))

colab_bot.add_handler(MessageHandler(upload_from_telegram, filters.command(["tupload"]) & filters.private & filters.regex(pattern=".*(https://t.me/.*)")))

colab_bot.add_handler(MessageHandler(gdrive_upload_from_url, filters.command(["gdupload"]) & filters.private & filters.regex(pattern=".*(drive.google.com|docs.google.com)")))

colab_bot.add_handler(MessageHandler(direct_upload_from_url, filters.command(["drupload"]) & filters.private))

colab_bot.add_handler(MessageHandler(leech_from_telegram, filters.command(["tleech"]) & filters.private & filters.regex(pattern=".*(https://t.me/.*)")))

colab_bot.add_handler(MessageHandler(unzip_from_telegram, filters.command(["t রাখি "]) & filters.private & filters.regex(pattern=".*(https://t.me/.*)")))

colab_bot.add_handler(MessageHandler(unzip_from_url, filters.command(["urlunzip"]) & filters.private))

colab_bot.add_handler(MessageHandler(set_rename_prefix, filters.command(["setname"]) & filters.private))

colab_bot.add_handler(MessageHandler(set_zip_password, filters.command(["zipaswd"]) & filters.private))

colab_bot.add_handler(MessageHandler(set_unzip_password, filters.command(["unzipaswd"]) & filters.private))

colab_bot.add_handler(CallbackQueryHandler(settings_handler, filters.regex('^setting')))
# Main handler for /tupload (handles both direct URLs and templates now)
colab_bot.add_handler(MessageHandler(upload_from_url, filters.command(["tupload"]) & filters.private))
colab_bot.add_handler(MessageHandler(leech_from_url, filters.command(["urlleech"]) & filters.private))
#——Handlers——
colab_bot.add_handler(MessageHandler(upload_from_telegram, filters.private & (filters.document | filters.video | filters.audio | filters.photo)))

print("Bot Started")
colab_bot.run()
