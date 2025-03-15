import os
import sys
from telethon import TelegramClient
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputMediaUploadedDocument

async def upload_file(file_path, bot_token, chat_id):
    
    client = TelegramClient('session_name', api_id=1, api_hash=54448a70ac7efd5cf70df608ec85cc8a)
    await client.start(bot_token=bot_token)

    try:
        
        file = await client.upload_file(file_path)
        media = InputMediaUploadedDocument(
            file=file,
            mime_type='application/octet-stream',
            attributes=[],
            thumb=None,
        )

        
        await client(SendMediaRequest(
            peer=chat_id,
            media=media,
            message="File uploaded from GitHub Actions",
        ))
        print("File uploaded successfully!")
    except Exception as e:
        print(f"Failed to upload file: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    import asyncio

    
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    
    asyncio.run(upload_file(file_path, bot_token, chat_id))
