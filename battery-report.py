from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


def load_token(filepath=".telegram.env"):
    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("Token not found in .telegram.env")


async def battery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
            level = f.read().strip()
        with open("/sys/class/power_supply/BAT0/status", "r") as f:
            status = f.read().strip()

        await update.message.reply_text(f"Battery: {level}% ({status})")
    except FileNotFoundError:
        await update.message.reply_text("Battery path not found on this system.")


token = load_token()
app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("battery", battery_command))
app.run_polling()
