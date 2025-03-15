from telethon import TelegramClient
import os
import sys

# Replace these with your own values
api_id = 24208636  # Your API ID
api_hash = '54448a70ac7efd5cf70df608ec85cc8a'  # Your API Hash

def upload_file(file_path, bot_token, chat_id):
    # Initialize the Telegram client
    client = TelegramClient('session_name', api_id, api_hash)

    async def main():
        try:
            # Connect to Telegram
            await client.start(bot_token=bot_token)

            # Upload the file
            await client.send_file(chat_id, file_path)
            print("File uploaded successfully!")
        except Exception as e:
            print(f"Failed to upload file: {e}")
        finally:
            # Disconnect the client
            await client.disconnect()

    # Run the async function
    with client:
        client.loop.run_until_complete(main())

if __name__ == "__main__":
    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Upload the file
    upload_file(file_path, bot_token, chat_id)
