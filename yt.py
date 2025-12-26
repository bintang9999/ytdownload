import os
import telebot
import yt_dlp
import time

# Ambil token dari Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **Bot Downloader Aktif!**\n\nKirimkan link TikTok, IG, atau YouTube. Aku akan kirimkan videonya buat kamu.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text
    if "http" not in url:
        return

    status_msg = bot.reply_to(message, "⏳ Sedang memproses link... Sabar ya.")
    
    # Setup folder download
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    filename_prefix = f"dl_{int(time.time())}"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Prioritas MP4 agar bisa diputar di HP
        'outtmpl': f'downloads/{filename_prefix}_%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'max_filesize': 48 * 1024 * 1024, # Limit sedikit di bawah 50MB
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            bot.edit_message_text("🚀 Sedang mendownload file...", message.chat.id, status_msg.message_id)
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            bot.edit_message_text("📤 Mengirim ke Telegram...", message.chat.id, status_msg.message_id)
            with open(file_path, 'rb') as video:
                bot.send_video(
                    message.chat.id, 
                    video, 
                    caption=f"✅ **Berhasil!**\n\n🎬 {info.get('title', 'Video')}\n🌐 Sumber: {info.get('extractor_key', 'Unknown')}",
                    supports_streaming=True
                )
            
            # Hapus file setelah terkirim
            if os.path.exists(file_path):
                os.remove(file_path)
            bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        error_msg = str(e)
        if "File is too large" in error_msg or "max_filesize" in error_msg:
            bot.edit_message_text("⚠️ Ukuran video terlalu besar (Lebih dari 50MB). Coba cari link video yang durasinya lebih pendek.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Gagal: {error_msg[:100]}...", message.chat.id, status_msg.message_id)
            
bot.infinity_polling()
