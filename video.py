import yt_dlp

def download_video(url):
    """
    Descarga un video de YouTube en formato MP4 de alta calidad
    en la carpeta actual
    
    Args:
        url (str): URL del video de YouTube
    """
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': '%(title).100s.%(ext)s',  # Limita el título a 100 caracteres
        'merge_output_format': 'mp4',
        'retries': 10,
        'socket_timeout': 30,
        'noplaylist': True,
        'restrictfilenames': True,  # Remueve caracteres especiales del nombre
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Iniciando descarga...")
            ydl.download([url])
            print("¡Descarga completada!")
            
    except Exception as e:
        print(f"Error en la descarga: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # URL del video
    video_url = 'https://youtu.be/6rvv8bU3pKA'
    
    # Descargar video en la carpeta actual
    download_video(video_url)