import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError

# Function to upload file using Telethon
async def upload_file(file_path, bot_token, chat_id):
    # Initialize the Telegram client
    client = TelegramClient('bot_session', api_id="2040", api_hash="b18441a1ff607e10a989891a5462e627")
    await client.start(bot_token=bot_token)

    try:
        # Convert chat_id to integer (if it's not already)
        chat_id = int(chat_id)

        # Upload the file
        await client.send_file(chat_id, file_path)
        print("File uploaded successfully!")
    except RPCError as e:
        print(f"Failed to upload file: {e}")
    except ValueError:
        print("Invalid chat ID. Please provide an integer chat ID.")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Run the async function
    asyncio.run(upload_file(file_path, bot_token, chat_id))
