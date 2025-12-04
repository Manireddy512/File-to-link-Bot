import os
from flask import Flask, request, send_from_directory
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-render-domain.onrender.com/webhook

app = Flask(__name__)
bot = Bot(BOT_TOKEN)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- BOT HANDLERS ----------------

async def start(update: Update, context):
    await update.message.reply_text("Send me any file and I will give a download link valid for 7 days.")

async def handle_file(update: Update, context):
    file = update.message.document or update.message.photo[-1] or update.message.video

    tg_file = await bot.get_file(file.file_id)

    filename = f"{int(time.time())}_{file.file_unique_id}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    await tg_file.download_to_drive(filepath)

    file_url = f"{request.url_root}download/{filename}"

    await update.message.reply_text(f"Your download link:\n{file_url}\n\nValid for 7 days.")

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_file))

# ---------------- FLASK ROUTES ----------------

@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.json, bot)
    await application.process_update(update)
    return "ok"

@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route("/")
def home():
    return "Bot is running"

# ---------------- STARTUP WEBHOOK SETTER ----------------

@app.before_request
def setup_webhook_once():
    if not hasattr(app, "webhook_set"):
        asyncio.get_event_loop().create_task(bot.set_webhook(url=WEBHOOK_URL + "/webhook"))
        app.webhook_set = True

# Export Flask app for Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
