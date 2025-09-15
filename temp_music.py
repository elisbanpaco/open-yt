import yt_dlp
import sys

url = 'https://youtu.be/_jRZQ1KgAwg'

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'retries': 10,
    'socket_timeout': 30,
    'noplaylist': True,
    'restrictfilenames': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("¡Descarga de música completada!")
except Exception as e:
    print(f"Error en la descarga: {e}")
    sys.exit(1)
