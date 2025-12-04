from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    # /start command
    if message.get("text") == "/start":
        send_message(chat_id, "Send me **any file** and I will give you a direct download link (valid 7 days).")
        return "ok"

    # Extract file_id from all possible places
    file_id = extract_file_id(message)

    if not file_id:
        send_message(chat_id, "⚠️ Could not detect a file. Try sending it normally (not as a restricted forward).")
        return "ok"

    # Retrieve file path from Telegram
    file_path = get_file_path(file_id)

    if file_path:
        download_link = f"{FILE_API}/{file_path}"
        send_message(chat_id, f"✔ Your download link (valid 7+ days):\n{download_link}")
    else:
        send_message(chat_id, "❌ Error: Could not retrieve file path from Telegram.")

    return "ok"


def extract_file_id(message):
    """
    Extracts file_id from any possible Telegram file type,
    including forwarded messages.
    """

    # Normal files
    if "document" in message:
        return message["document"]["file_id"]
    if "video" in message:
        return message["video"]["file_id"]
    if "photo" in message:
        return message["photo"][-1]["file_id"]
    if "audio" in message:
        return message["audio"]["file_id"]
    if "voice" in message:
        return message["voice"]["file_id"]
    if "video_note" in message:
        return message["video_note"]["file_id"]
    if "animation" in message:
        return message["animation"]["file_id"]

    # Forwarded messages sometimes hide file info
    fwd = message.get("forward_origin", {})

    if "document" in fwd:
        return fwd["document"]["file_id"]
    if "video" in fwd:
        return fwd["video"]["file_id"]
    if "photo" in fwd:
        return fwd["photo"][-1]["file_id"]

    return None


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def get_file_path(file_id):
    url = f"{BASE_URL}/getFile"
    response = requests.get(url, params={"file_id": file_id}).json()
    
    logging.info(f"getFile response: {response}")

    try:
        return response["result"]["file_path"]
    except:
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
