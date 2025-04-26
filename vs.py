from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import paramiko
import os

# Store user data temporarily
user_data = {}

REPO_URL = "https://github.com/gx7owner/bg.git"  # Replace with your repo
REPO_NAME = "bg"  # Replace with your repo name (folder name after clone)
FINAL_COMMAND = "pip install telebot flask aiogram pyTelegramBotAPI python-telegram-bot pytz psutil motor && chmod +x * && nohup python3 g.py &> /dev/null &"  # Change this if needed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" 𝐘𝐎𝐔𝐑 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐒𝐈𝐑 𝐈𝐍 𝐆𝐱𝟕 𝐕𝐏𝐒 𝐒𝐄𝐓𝐔𝐏 𝐁𝐎𝐓\n𝐁𝐄𝐒𝐓 𝐁𝐎𝐓 𝐓𝐎 𝐌𝐀𝐊𝐄 𝐘𝐎𝐔𝐑 𝐎𝐖𝐍 𝐃𝐃𝐎𝐒 𝐁𝐎𝐓 𝐈𝐍 𝟓 𝐒𝐄𝐂𝐎𝐍𝐃\n /vpsip, /vpsuser, /vpspass, /token, /adminid to configure your VPS.\n\n𝐓𝐇𝐈𝐒 𝐁𝐎𝐓 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 @Gx7_Owner")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()[0][1:]
    await update.message.reply_text(f"Send me the value for {cmd}")
    user_data[update.message.chat_id] = user_data.get(update.message.chat_id, {})
    user_data[update.message.chat_id]['awaiting'] = cmd

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

async def setup_vps(update: Update, data):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(data['vpsip'], username=data['vpsuser'], password=data['vpspass'])

        commands = [
            f"git clone {REPO_URL}",
            f"cd {REPO_NAME} && sed -i '12s/.*/BOT_TOKEN = \"{data['token']}\"/' g.py",
            f"cd {REPO_NAME} && sed -i '13s/.*/ADMIN_ID = [{data['adminid']}]/' g.py",
            f"cd {REPO_NAME} && {FINAL_COMMAND}"
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.read().decode()
            out = stdout.read().decode()
            if err:
                await update.message.reply_text(f"Error: {err}")
            else:
                await update.message.reply_text(f"Executed: {cmd}\nOutput: {out.strip()}")

        ssh.close()
        await update.message.reply_text("VPS setup and execution complete.")

    except Exception as e:
        await update.message.reply_text(f"Failed: {str(e)}")

def main():
    bot_token = "7666185256:AAFVXOwn6Zuh2rldNIOnCaprIfxAUnTVQ2I"  # <--- Put your main bot token here
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    for cmd in ['vpsip', 'vpsuser', 'vpspass', 'token', 'adminid']:
        app.add_handler(CommandHandler(cmd, handle_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
  
