# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import asyncio
import logging
import os
import sys
from pyrogram import Client
from colab_leecher.utility.variables import BOT, Var
from colab_leecher.utility.task_manager import task_starter

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

# --- Initialize the Bot ---
if Var.work_at == "colab":
    colab_bot = Client(
        "my_bot",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN,
        plugins=dict(root="colab_leecher.plugins"),
    )
elif Var.work_at == "local":
    colab_bot = Client(
        "my_bot",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        plugins=dict(root="colab_leecher.plugins"),
    )


# --- Telegram Client Event Handlers ---

@colab_bot.on_message()  # Handles all incoming messages
async def on_message(client, message):
    if int(message.from_user.id) != int(Var.USER_ID):  # type: ignore
        await client.send_message(
            text="**Sorry You're Not Authorized!**",
            chat_id=message.from_user.id,  # type: ignore
        )
        return  # Exit handler if unauthorized user

    # Start the bot's task if a /urlleech or /gdupload command is received
    if (
        message.text == "/urlleech"
        or message.text == "/gdupload"
        or message.text == "/tupload"
    ):
        await task_starter(client, message)
    elif BOT.State.waiting_for_input:
        await task_starter(client, message)  # Pass message to task_manager
    elif message.text == "/cancel":
        await task_starter(client, message)  # Pass message to task_manager for handling.

# --- Main Function (Runs the Bot) ---
def main():
    try:
        if Var.work_at == "local" and os.path.exists("my_bot.session"):
            os.remove("my_bot.session")
        colab_bot.run()  # Starts the Telegram client (blocking)

    except (KeyboardInterrupt, SystemExit):
        LOG.info("Bot stopped. Exiting.")
        sys.exit()

if __name__ == "__main__":
    main()
