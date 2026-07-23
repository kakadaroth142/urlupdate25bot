# urlupdate25bot
Repository name: urlupdate25bot
Description: Bot ទាញវិដេអូ
Visibility: Public ✅
Initialize with README ✅
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, asyncio, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
from config import BOT_TOKEN, DOWNLOAD_FOLDER

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
            return {
                'ok': True,
                'title': info.get('title', 'វិដេអូ'),
                'file': ydl.prepare_filename(info)
            }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e)
        }

async def start(u, c):
    await u.message.reply_text(
        "🎥 <b>Bot ទាញវិដេអូ Urlupdate25</b>\n\n"
        "📥 វាង URL វិដេអូ\n\n"
        "/help - ជំនួយលម្អិត",
        parse_mode='HTML'
    )

async def help_cmd(u, c):
    await u.message.reply_text(
        "📚 <b>ជំនួយលម្អិត</b>\n\n"
        "🔹 480p - លឿនបំផុត ⚡\n"
        "🔹 720p - មធ្យម ⭐\n"
        "🔹 1080p - ល្អបំផុត 🎬\n\n"
        "👤 ទាក់ទងបញ្ហា: @KAKADAROTHKH01",
        parse_mode='HTML'
    )

async def handle_msg(u, c):
    url = u.message.text.strip()
    if not url.startswith('http'):
        await u.message.reply_text("❌ សូមវាង URL ដែលត្រឹមត្រូវ")
        return
    
    c.user_data['url'] = url
    
    kb = [
        [InlineKeyboardButton("480p ⚡", callback_data="480"), InlineKeyboardButton("720p ⭐", callback_data="720")],
        [InlineKeyboardButton("1080p 🎬", callback_data="1080")]
    ]
    
    await u.message.reply_text(
        "📊 ជ្រើសរើស Resolution:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

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
        await q.edit_message_text(
            f"✅ <b>ទាញរួច!</b>\n\n"
            f"📝 ចំណងជើង: {r['title'][:50]}\n"
            f"📊 Resolution: {res}p\n"
            f"📁 ឯកសារ: {os.path.basename(r['file'])}",
            parse_mode='HTML'
        )
    else:
        await q.edit_message_text(
            f"❌ <b>មានលម្អិត:</b>\n{r['error'][:150]}",
            parse_mode='HTML'
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
app.add_handler(CallbackQueryHandler(btn))

print("\n" + "="*60)
print("🚀 Bot ទាញវិដេអូ Urlupdate25 កំពុងចាប់ផ្តើម...")
print("="*60 + "\n")
print("✅ Bot រួចរាល់!\n")
print("🎯 ចាប់ផ្តើមស្ដាប់...\n")

app.run_polling()
