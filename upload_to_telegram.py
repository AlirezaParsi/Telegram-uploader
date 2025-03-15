import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

def upload_file(file_path, bot_token, chat_id):
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > 2000 * 1024 * 1024:  # 2 GB limit
        raise ValueError("File size exceeds Telegram's 2 GB limit.")

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Create a multipart encoder for chunked uploads
        multipart_data = MultipartEncoder(
            fields={
                "chat_id": chat_id,
                "document": (os.path.basename(file_path), file, "application/octet-stream"),
            }
        )

        # Send the file to Telegram
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
        )

    # Check the response
    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.text}")
    else:
        print("File uploaded successfully!")

if __name__ == "__main__":
    import sys

    # Get arguments
    file_path = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    # Upload the file
    upload_file(file_path, bot_token, chat_id)
