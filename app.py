import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# In PTB v21+ → Application.builder() replaced by ApplicationBuilder()
application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context):
    await update.message.reply_text("Send any file and I will return a download link!")


async def handle_file(update: Update, context):
    message = update.message

    file_obj = (
        message.document
        or (message.photo[-1] if message.photo else None)
        or message.video
        or message.audio
        or message.voice
    )

    if not file_obj:
        await message.reply_text("Please send a valid file.")
        return

    file = await context.bot.get_file(file_obj.file_id)

    # Telegram link automatically works for 7+ days
    download_link = file.file_path

    await message.reply_text(f"Download link:\n{download_link}\n\n(Valid for at least 7 days)")


@app.post("/webhook")
def webhook():
    update = Update.de_json(request.json, application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


@app.get("/")
def home():
    return "Bot running!", 200


@app.before_first_request
def init_webhook():
    application.bot.set_webhook(WEBHOOK_URL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
