import os
from flask import Flask, request, send_from_directory
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import asyncio

BOT_TOKEN = "8346484698:AAEZWFCCPUbnNksHUSkOP7CuQeaAke5YenE"
BOT_USERNAME = "file_to_link_mine_bot"  # without @
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask(__name__)

# ===========================
#  Serve Uploaded Files
# ===========================
@app.route("/file/<path:filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)


# ===========================
#  Telegram Webhook Handler
# ===========================
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    file_obj = (
        message.document or
        (message.photo[-1] if message.photo else None) or
        message.video
    )

    if not file_obj:
        await message.reply_text("Send me any file and I’ll give you a download link.")
        return

    # download file
    file_id = file_obj.file_id
    telegram_file = await context.bot.get_file(file_id)

    filename = file_obj.file_unique_id
    file_path = os.path.join(UPLOAD_DIR, filename)

    await telegram_file.download_to_drive(file_path)

    # Render domain will be something like
    # https://your-app.onrender.com
    server_url = os.environ.get("https://file-to-link-bot-uqxp.onrender.com", "")

    download_link = f"{server_url}/file/{filename}"

    await message.reply_text(f"Here is your download link (valid for 7 days):\n{download_link}")


telegram_app.add_handler(MessageHandler(filters.ALL, handle_file))


@app.route(f"/{BOT_USERNAME}", methods=['POST'])
def webhook():
    """Receive webhook updates from Telegram"""
    data = request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok"


# ===========================
#  Start Flask Server
# ===========================
if __name__ == "__main__":
    print("Starting combined server + bot...")
    telegram_app.bot.set_webhook(url=f"{os.environ.get('RENDER_EXTERNAL_URL')}/{BOT_USERNAME}")
    app.run(host="0.0.0.0", port=10000)
