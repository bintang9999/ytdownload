import os
import telebot
import yt_dlp

# Ambil token dari Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Kirimkan link video (TikTok/IG/YT), nanti aku download-in!")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "http" not in url:
        return

    msg = bot.reply_to(message, "⏳ Sedang memproses... Tunggu bentar ya.")
    
    # Folder tempat simpan sementara
    output_dir = "downloads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024, # Batas 50MB agar tidak ditolak Telegram
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=info.get('title', 'Video Berhasil didownload!'))
            
            # Hapus file setelah dikirim agar penyimpanan Railway tidak penuh
            os.remove(filename)
            bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id)

bot.polling()