
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, asyncio, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = "8977687420:AAHsKSrMxYU56sPJuI8dFSz6XZQY6CypSoU"
DOWNLOAD_FOLDER = "/tmp/videos"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def download_video(url, res="720"):
    try:
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        opts = {
            'format': f'best[height<={res}]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': False
        }
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            return {'ok': True, 'title': info.get('title'), 'file': ydl.prepare_filename(info)}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

async def start(u, c):
    await u.message.reply_text("🎥 <b>Bot ទាញវិដេអូ Urlupdate25</b>\n\nវាង URL វិដេអូ\n\n/help - ជំនួយ", parse_mode='HTML')

async def help_cmd(u, c):
    await u.message.reply_text("📚 វាង URL ហើយជ្រើស Resolution\n\n480p ⚡ | 720p ⭐ | 1080p 🎬")

async def handle_msg(u, c):
    url = u.message.text.strip()
    if not url.startswith('http'):
        await u.message.reply_text("❌ URL មិនត្រឹមត្រូវ")
        return
    c.user_data['url'] = url
    kb = [
        [InlineKeyboardButton("480p ⚡", callback_data="480"), InlineKeyboardButton("720p ⭐", callback_data="720")],
        [InlineKeyboardButton("1080p 🎬", callback_data="1080")]
    ]
    await u.message.reply_text("📊 ជ្រើសរើស Resolution:", reply_markup=InlineKeyboardMarkup(kb))

async def btn(u, c):
    q = u.callback_query
    await q.answer()
    res = q.data
    url = c.user_data.get('url')
    if not url:
        await q.edit_message_text("❌ URL មិនរកឃើញ")
        return
    await q.edit_message_text(f"⏳ កំពុងទាញ {res}p...\nសូមរង់ចាំ...")
    r = await download_video(url, res)
    if r['ok']:
        await q.edit_message_text(f"✅ <b>ទាញរួច!</b>\n\n📝 ចំណងជើង: {r['title'][:50]}\n📊 Resolution: {res}p", parse_mode='HTML')
    else:
        await q.edit_message_text(f"❌ មានលម្អិត:\n{r['error'][:100]}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
app.add_handler(CallbackQueryHandler(btn))

print("🚀 Bot ទាញវិដេអូ Urlupdate25 កំពុងចាប់ផ្តើម...\n")
app.run_polling()
