import os
import sys
import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def upload_file(file_path, bot_token, chat_id):
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > 2000 * 1024 * 1024:  # 2 GB limit
        raise ValueError("File size exceeds Telegram's 2 GB limit.")

    # Initialize the bot
    bot = Bot(token=bot_token)

    try:
        # Upload the file
        with open(file_path, "rb") as file:
            await bot.send_document(chat_id=chat_id, document=file)
        print("File uploaded successfully!")
    except TelegramError as e:
        print(f"Failed to upload file: {e}")

if __name__ == "__main__":
    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Run the async function
    asyncio.run(upload_file(file_path, bot_token, chat_id))
