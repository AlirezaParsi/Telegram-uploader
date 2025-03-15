import os
import sys
import requests

def upload_file(file_path, bot_token, chat_id):
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > 2000 * 1024 * 1024:  # 2 GB limit
        raise ValueError("File size exceeds Telegram's 2 GB limit.")

    # Telegram API URL
    api_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    try:
        # Upload the file
        with open(file_path, "rb") as file:
            response = requests.post(
                api_url,
                data={"chat_id": chat_id},
                files={"document": file}
            )
        
        # Check if the upload was successful
        if response.status_code == 200:
            print("File uploaded successfully!")
        else:
            print(f"Failed to upload file. Telegram API response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Upload the file
    upload_file(file_path, bot_token, chat_id)
