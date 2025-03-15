import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError

# Function to upload file using Telethon
async def upload_file(file_path, bot_token, chat_id):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    # Initialize the Telegram client
    client = TelegramClient('bot_session', api_id=2040, api_hash="b18441a1ff607e10a989891a5462e627")
    await client.start(bot_token=bot_token)

    try:
        # Convert chat_id to integer (if it's not already)
        chat_id = int(chat_id)

        # Extract the filename from the file path
        file_name = os.path.basename(file_path)

        # Set the caption to the original filename
        caption = f"File: {file_name}"

        # Check file size (Telegram limit is 2 GB for bots)
        file_size = os.path.getsize(file_path)
        if file_size > 2000 * 1024 * 1024:  # 2 GB limit
            raise ValueError("File size exceeds Telegram's 2 GB limit for bots.")

        # Upload the file with the correct filename and caption
        await client.send_file(
            chat_id,
            file_path,
            caption=caption,
            file_name=file_name,
            part_size_kb=512,  # Adjust chunk size for better upload performance
            force_document=True  # Force upload as a document
        )
        print("File uploaded successfully with correct filename and caption!")
    except RPCError as e:
        print(f"Failed to upload file: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Run the async function
    asyncio.run(upload_file(file_path, bot_token, chat_id))
