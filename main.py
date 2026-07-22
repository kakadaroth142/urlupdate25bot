#!/usr/bin/env python3
"""
Urlupdate25 Bot - Video Download Bot
ទាញវិដេអូ bot
"""

import logging
import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, DOWNLOAD_FOLDER, ADMIN_ID, START_MESSAGE, HELP_MESSAGE

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create download folder if not exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(START_MESSAGE)
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    await update.message.reply_text(HELP_MESSAGE)


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download video from URL"""
    url = update.message.text.strip()
    
    # Check if URL is valid
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ មិនត្រូវ URL!\nPlease send a valid URL starting with http:// or https://")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("⏳ កំពុងទាញវិដេអូ...\nDownloading video...")
    
    try:
        # Use yt-dlp to download video
        output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")
        
        command = [
            "yt-dlp",
            "-f", "best",
            "-o", output_template,
            url
        ]
        
        logger.info(f"Downloading from {url}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            await processing_msg.edit_text(f"❌ មានបញ្ហា!\nError: {result.stderr[:200]}")
            logger.error(f"Download failed: {result.stderr}")
            return
        
        # Find downloaded file
        files = os.listdir(DOWNLOAD_FOLDER)
        if not files:
            await processing_msg.edit_text("❌ មិនបានរកឃើញឯកសារ!")
            return
        
        video_file = os.path.join(DOWNLOAD_FOLDER, files[-1])
        file_size = os.path.getsize(video_file)
        
        # Check file size
        if file_size > 2147483648:  # 2GB limit for Telegram
            await processing_msg.edit_text("❌ ឯកសារធំពេក! (Max 2GB)")
            os.remove(video_file)
            return
        
        # Send video
        await processing_msg.edit_text("📤 ផ្ញើវិដេអូ...")
        
        with open(video_file, 'rb') as video:
            await update.message.reply_video(video, caption="✅ ដោះស្រាយ!")
        
        # Cleanup
        os.remove(video_file)
        await processing_msg.delete()
        
        logger.info(f"Successfully downloaded from {url}")
        
    except subprocess.TimeoutExpired:
        await processing_msg.edit_text("⏱️ ដោះស្រាយយូរពេក!\nTimeout - try again later")
        logger.error("Download timeout")
    except Exception as e:
        await processing_msg.edit_text(f"❌ មានកំហុស!\nError: {str(e)[:200]}")
        logger.error(f"Error: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    logger.info("Starting Urlupdate25 Bot...")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
