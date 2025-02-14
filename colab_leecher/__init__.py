import logging
import json
from uvloop import install
from pyrogram.client import Client

# Install uvloop to optimize asyncio
install()

# Read credentials from the JSON file
def load_credentials(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Initialize logging
def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Setup bot client
def initialize_bot(credentials):
    return Client("my_bot", api_id=credentials["API_ID"], api_hash=credentials["API_HASH"], bot_token=credentials["BOT_TOKEN"])

# Main function to run everything
def main():
    setup_logging()

    # Load credentials
    credentials = load_credentials("/content/Telegram-Leecher/credentials.json")

    # Initialize bot with credentials
    colab_bot = initialize_bot(credentials)

    # Now you can proceed with your bot operations, using `colab_bot`
    logging.info("Bot initialized successfully.")
    
    return colab_bot

# Run the bot
if __name__ == "__main__":
    colab_bot = main()
    colab_bot.run()  # Start the bot
