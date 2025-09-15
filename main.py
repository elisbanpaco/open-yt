import yt_dlp

url = 'https://youtu.be/A953td1sKS8'

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    # 'socket_timeout': 30,  # Aumentar el tiempo de espera en segundos
    # 'retries': 10,         # Intentar más veces
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
