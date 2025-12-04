import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-app.onrender.com/webhook

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context):
    await update.message.reply_text("Send me any file and I will give you a download link!")


async def handle_file(update: Update, context):
    file_obj = None

    if update.message.document:
        file_obj = update.message.document
    elif update.message.photo:
        file_obj = update.message.photo[-1]
    elif update.message.video:
        file_obj = update.message.video

    if not file_obj:
        await update.message.reply_text("Please send a valid file.")
        return

    file_id = file_obj.file_id
    file = await context.bot.get_file(file_id)

    # important: Telegram stores it for at least a week
    download_link = file.file_path

    await update.message.reply_text(f"Here is your download link:\n\n{download_link}\n\nValid for 7+ days.")


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.json, telegram_app.bot)
    telegram_app.process_update(update)
    return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return "Telegram File Bot Running", 200


# Set webhook when app starts on Render
@app.before_first_request
def setup_webhook():
    telegram_app.bot.set_webhook(url=WEBHOOK_URL)


# Gunicorn needs this
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
