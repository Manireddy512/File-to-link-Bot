from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    # Start command
    if "text" in message and message["text"] == "/start":
        send_message(chat_id, "Send me any file and I will give you a direct download link.")
        return "ok"

    # If file is sent
    file_id = None
    if "document" in message:
        file_id = message["document"]["file_id"]
    elif "video" in message:
        file_id = message["video"]["file_id"]
    elif "audio" in message:
        file_id = message["audio"]["file_id"]
    elif "photo" in message:
        file_id = message["photo"][-1]["file_id"]  # highest resolution

    if file_id:
        file_path = get_file_path(file_id)
        if file_path:
            download_link = f"{FILE_API}/{file_path}"
            send_message(chat_id, f"Here is your file link (valid for at least 1 week):\n\n{download_link}")
        else:
            send_message(chat_id, "Failed to retrieve the file path.")
    
    return "ok"


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def get_file_path(file_id):
    url = f"{BASE_URL}/getFile?file_id={file_id}"
    response = requests.get(url).json()
    try:
        return response["result"]["file_path"]
    except:
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
