from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import paramiko
import json

# Store user data temporarily
user_data = {}

REPO_URL = "https://github.com/gx7owner/bg.git"
REPO_NAME = "bg"
FINAL_COMMAND = (
    "pip install telebot flask aiogram pyTelegramBotAPI python-telegram-bot pytz psutil motor "
    "&& chmod +x * && nohup python3 g.py &> /dev/null &"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " 𝐘𝐎𝐔𝐑 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐒𝐈𝐑 𝐈𝐍 𝐆𝐱𝟕 𝐕𝐏𝐒 𝐒𝐄𝐓𝐔𝐏 𝐁𝐎𝐓\n"
        "𝐁𝐄𝐒𝐓 𝐁𝐎𝐓 𝐓𝐎 𝐌𝐀𝐊𝐄 𝐘𝐎𝐔𝐑 𝐎𝐖𝐍 𝐃𝐃𝐎𝐒 𝐁𝐎𝐓 𝐈𝐍 𝟓 𝐒𝐄𝐂𝐎𝐍𝐃\n"
        "/vpsip, /vpsuser, /vpspass, /token, /adminid to configure your VPS.\n\n"
        "𝐓𝐇𝐈𝐒 𝐁𝐎𝐓 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 @Gx7_Owner"
    )

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()[0][1:]
    await update.message.reply_text(f"Send me the value for {cmd}")
    chat_id = update.message.chat_id
    user_data[chat_id] = user_data.get(chat_id, {})
    user_data[chat_id]['awaiting'] = cmd

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in user_data or 'awaiting' not in user_data[chat_id]:
        return await update.message.reply_text("Please start with /vpsip or another command.")

    key = user_data[chat_id]['awaiting']
    user_data[chat_id][key] = update.message.text
    del user_data[chat_id]['awaiting']
    await update.message.reply_text(f"{key} saved.")

    required_keys = ['vpsip', 'vpsuser', 'vpspass', 'token', 'adminid']
    if all(k in user_data[chat_id] for k in required_keys):
        await update.message.reply_text("All data received. Connecting to VPS...")
        await setup_vps(update, user_data[chat_id])

async def send_long_message(update, text):
    max_length = 4000
    for i in range(0, len(text), max_length):
        await update.message.reply_text(text[i:i+max_length])

async def setup_vps(update: Update, data):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(data['vpsip'], username=data['vpsuser'], password=data['vpspass'])

        # Prepare JSON config string
        config_content = json.dumps({
            "BOT_TOKEN": data['token'],
            "ADMIN_ID": int(data['adminid'])
        })

        commands = [
            f"git clone {REPO_URL}",
            f"cd {REPO_NAME} && echo '{config_content}' > config.json",
            f"cd {REPO_NAME} && {FINAL_COMMAND}"
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.read().decode()
            out = stdout.read().decode()
            if err.strip():
                await send_long_message(update, f"Error: {err.strip()}")
            else:
                await send_long_message(update, f"Executed: {cmd}\nOutput: {out.strip()}")

        ssh.close()
        await update.message.reply_text("VPS setup and execution complete.")

    except Exception as e:
        await send_long_message(update, f"Failed: {str(e)}")

def main():
    bot_token = "7721614824:AAGfQqCpE9zmD38b2Xq1nyiI7yqBNKV0wDg"
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    for cmd in ['vpsip', 'vpsuser', 'vpspass', 'token', 'adminid']:
        app.add_handler(CommandHandler(cmd, handle_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
    
