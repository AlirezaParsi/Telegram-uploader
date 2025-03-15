import os
import sys
import asyncio
import subprocess
import re
from telethon import TelegramClient
from telethon.errors import RPCError

# Function to send a message to Telegram
async def send_message(bot_token, chat_id, text):
    client = TelegramClient('bot_session', api_id=2040, api_hash="b18441a1ff607e10a989891a5462e627")
    await client.start(bot_token=bot_token)
    try:
        await client.send_message(int(chat_id), text, parse_mode="markdown")  # Enable Markdown formatting
    except RPCError as e:
        print(f"Failed to send message: {e}")
    finally:
        await client.disconnect()

# Function to extract file ID from Google Drive URL
def extract_gdrive_file_id(url):
    # Handle different Google Drive URL formats
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",  # Standard URL format
        r"id=([a-zA-Z0-9_-]+)",       # Export URL format
        r"open\?id=([a-zA-Z0-9_-]+)",  # Open URL format
        r"download\?id=([a-zA-Z0-9_-]+)"  # Download URL format
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid Google Drive URL format")

# Function to download a file from Google Drive
def download_gdrive_file(url, output):
    file_id = extract_gdrive_file_id(url)  # Extract file ID from URL
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    subprocess.run(["wget", "--no-check-certificate", "-O", output, download_url], check=True)

# Function to download a file
def download_file(download_url, download_type, mega_email, mega_password, rclone_config):
    file_name = os.path.basename(download_url)
    if download_type == "video":
        # Use yt-dlp for videos
        subprocess.run(["yt-dlp", "-o", "%(title)s.%(ext)s", download_url], check=True)
        file_name = subprocess.run(
            ["yt-dlp", "--get-filename", "-o", "%(title)s.%(ext)s", download_url],
            capture_output=True, text=True
        ).stdout.strip()
    elif download_type == "cloud":
        if "drive.google.com" in download_url or "google.com" in download_url:
            # Handle Google Drive links
            download_gdrive_file(download_url, file_name)
        elif "mega.nz" in download_url:
            subprocess.run(
                ["megadl", download_url, "--username", mega_email, "--password", mega_password, "--path", file_name],
                check=True
            )
        elif "dropbox.com" in download_url:
            subprocess.run(
                ["curl", "-o", file_name, download_url.replace("dl=0", "dl=1")],
                check=True
            )
        elif "onedrive.live.com" in download_url or "1drv.ms" in download_url:
            with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "w") as f:
                f.write(rclone_config)
            subprocess.run(
                ["rclone", "copyurl", download_url, "./", "--config", os.path.expanduser("~/.config/rclone/rclone.conf")],
                check=True
            )
            file_name = subprocess.run(
                ["ls", "-t"], capture_output=True, text=True
            ).stdout.splitlines()[0].strip()
        else:
            raise ValueError("Unsupported cloud link.")
    else:
        # Handle direct links using aria2c
        subprocess.run(["aria2c", "-o", file_name, download_url], check=True)

    # Verify the file exists
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"File not found: {file_name}")

    return file_name

# Function to split a file into smaller parts
def split_file(file_path, part_size_mb=1500):
    part_size_bytes = part_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = os.path.getsize(file_path)
    if file_size <= part_size_bytes:
        return [file_path]  # No need to split

    # Split the file
    part_prefix = f"{file_path}_part_"
    subprocess.run(["split", "-b", f"{part_size_bytes}", file_path, part_prefix], check=True)

    # Get the list of parts
    parts = sorted([f for f in os.listdir() if f.startswith(part_prefix)])
    return parts

# Function to upload a file to Telegram
async def upload_file(file_path, bot_token, chat_id, caption=None):
    # Initialize the Telegram client
    client = TelegramClient('bot_session', api_id=2040, api_hash="b18441a1ff607e10a989891a5462e627")
    await client.start(bot_token=bot_token)

    try:
        # Convert chat_id to integer (if it's not already)
        chat_id = int(chat_id)

        # Extract the filename from the file path
        file_name = os.path.basename(file_path)

        # Set the caption to the original filename if not provided
        if caption is None:
            caption = f"File: {file_name}"

        # Upload the file with the correct filename and caption
        await client.send_file(
            chat_id,
            file_path,
            caption=caption,
            file_name=file_name,
            part_size_kb=512,  # Adjust chunk size for better upload performance
            force_document=True  # Force upload as a document
        )
        print(f"File part uploaded successfully: {file_name}")
    except RPCError as e:
        print(f"Failed to upload file: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await client.disconnect()

# Main function
async def main():
    # Get arguments
    download_url = sys.argv[1]
    download_type = sys.argv[2]
    bot_token = sys.argv[3]
    chat_id = sys.argv[4]
    mega_email = sys.argv[5]
    mega_password = sys.argv[6]
    rclone_config = sys.argv[7]

    # Initialize file_path to avoid UnboundLocalError
    file_path = None
    parts = []

    try:
        # Notify download started with hyperlink
        await send_message(bot_token, chat_id, f"📥 Download started: [Click here]({download_url})")

        # Download the file
        file_path = download_file(download_url, download_type, mega_email, mega_password, rclone_config)

        # Notify download finished
        file_size = os.path.getsize(file_path)
        md5_checksum = subprocess.run(
            ["md5sum", file_path], capture_output=True, text=True
        ).stdout.split()[0]
        await send_message(
            bot_token, chat_id,
            f"✅ Download finished: `{file_path}`\nSize: `{file_size / 1024 / 1024:.2f} MB`\nMD5: `{md5_checksum}`"
        )

        # Split the file into smaller parts if it's larger than 2 GB
        parts = split_file(file_path)
        if len(parts) > 1:
            await send_message(bot_token, chat_id, f"📦 Splitting file into {len(parts)} parts...")

        # Upload each part
        for part in parts:
            await send_message(bot_token, chat_id, f"📤 Uploading part: `{part}`")
            await upload_file(part, bot_token, chat_id, caption=f"Part: `{part}`")

        # Notify upload finished
        await send_message(
            bot_token, chat_id,
            f"✅ Upload finished: `{file_path}`\nSize: `{file_size / 1024 / 1024:.2f} MB`\nMD5: `{md5_checksum}`"
        )

    except Exception as e:
        # Notify error
        await send_message(bot_token, chat_id, f"❌ Error: `{e}`")
        raise e
    finally:
        # Clean up
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        for part in parts:
            if os.path.exists(part):
                os.remove(part)

if __name__ == "__main__":
    asyncio.run(main())
