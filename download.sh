#!/bin/bash

# Script para facilitar la descarga de música y videos desde YouTube
# Autor: Script automatizado para music-free

# Colores para la interfaz
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar el menú principal
show_menu() {
    clear
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    DESCARGADOR YOUTUBE         ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${YELLOW}1)${NC} Descargar música (MP3)"
    echo -e "${YELLOW}2)${NC} Descargar video (MP4)"
    echo -e "${YELLOW}3)${NC} Salir"
    echo ""
    echo -e "${GREEN}Selecciona una opción:${NC} "
}

# Función para descargar música
download_music() {
    echo -e "${GREEN}Ingresa la URL del video/música:${NC} "
    read url
    
    if [ -z "$url" ]; then
        echo -e "${RED}Error: URL vacía${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Iniciando descarga de música...${NC}"
    
    # Crear script temporal de Python para música
    cat > temp_music.py << EOF
import yt_dlp
import sys

url = '$url'

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
EOF
    
    python3 temp_music.py
    rm temp_music.py
}

# Función para descargar video
download_video() {
    echo -e "${GREEN}Ingresa la URL del video:${NC} "
    read url
    
    if [ -z "$url" ]; then
        echo -e "${RED}Error: URL vacía${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Iniciando descarga de video...${NC}"
    
    # Crear script temporal de Python para video
    cat > temp_video.py << EOF
import yt_dlp
import sys

url = '$url'

ydl_opts = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
    'outtmpl': '%(title).100s.%(ext)s',
    'merge_output_format': 'mp4',
    'retries': 10,
    'socket_timeout': 30,
    'noplaylist': True,
    'restrictfilenames': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("¡Descarga de video completada!")
except Exception as e:
    print(f"Error en la descarga: {e}")
    sys.exit(1)
EOF
    
    python3 temp_video.py
    rm temp_video.py
}

# Verificar dependencias
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python3 no está instalado${NC}"
        exit 1
    fi
    
    if ! python3 -c "import yt_dlp" &> /dev/null; then
        echo -e "${RED}Error: yt-dlp no está instalado${NC}"
        echo -e "${YELLOW}Instala con: pip install yt-dlp${NC}"
        exit 1
    fi
}

# Función principal
main() {
    # Verificar dependencias
    check_dependencies
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                download_music
                echo -e "${GREEN}Presiona Enter para continuar...${NC}"
                read
                ;;
            2)
                download_video
                echo -e "${GREEN}Presiona Enter para continuar...${NC}"
                read
                ;;
            3)
                echo -e "${GREEN}¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                sleep 2
                ;;
        esac
    done
}

# Ejecutar programa principal
main