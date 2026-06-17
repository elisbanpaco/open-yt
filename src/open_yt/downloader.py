from pathlib import Path
from typing import Any, Dict, Optional

import yt_dlp

from open_yt.config import Settings
from open_yt.i18n import _
from open_yt.ui import ProgressHook, console, show_media_info, get_status_spinner


class MediaDownloader:
    """Clase principal para descargas de medios usando yt-dlp."""

    def __init__(self) -> None:
        """Inicializa el descargador con la configuración."""
        self.settings = Settings.load()
        self._ydl_opts: Dict[str, Any] = {}

    _THUMB_FORMATS = {"mp3", "m4a", "flac", "ogg", "opus"}

    def _get_audio_opts(self, quality: str, output_path: Path) -> Dict[str, Any]:
        """Genera opciones de yt-dlp para descarga de audio."""
        codec = self.settings.default_audio_format
        embed = self.settings.embed_thumbnail and codec in self._THUMB_FORMATS

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": quality,
            }
        ]

        if embed:
            postprocessors.append({"key": "EmbedThumbnail"})

        postprocessors.append({
            "key": "FFmpegMetadata",
            "add_metadata": True,
        })

        return {
            "format": "bestaudio/best",
            "outtmpl": str(output_path / "%(title)s.%(ext)s"),
            "postprocessors": postprocessors,
            "writethumbnail": embed,
            "embedthumbnail": embed,
            "progress_hooks": [ProgressHook()],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

    def _get_video_opts(self, quality: str, output_path: Path) -> Dict[str, Any]:
        """Genera opciones de yt-dlp para descarga de video."""
        format_str = f"bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "best"
        return {
            "format": format_str,
            "outtmpl": str(output_path / "%(title)s.%(ext)s"),
            "progress_hooks": [ProgressHook()],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

    def _extract_info(self, url: str) -> Dict[str, Any]:
        """Extrae metadatos del video sin descargar."""
        opts: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "noplaylist": True,
        }
        with get_status_spinner(_("Extracting metadata...")):
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError(_("Could not retrieve video information"))
                return info

    def _show_info(self, info: Dict[str, Any]) -> None:
        """Muestra los metadatos del video en una tabla."""
        display_info: Dict[str, Any] = {
            "title": info.get("title", "N/A"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", info.get("channel", "N/A")),
            "upload_date": info.get("upload_date", "N/A"),
            "view_count": info.get("view_count", 0),
            "like_count": info.get("like_count", 0),
        }
        if "resolution" in info:
            display_info["resolution"] = info["resolution"]
        if "format" in info:
            display_info["format"] = info["format"]

        show_media_info(display_info)

    def download_audio(
        self,
        url: str,
        quality: Optional[str] = None,
        output: Optional[Path] = None,
    ) -> bool:
        """Descarga audio de YouTube."""
        output_path = output or self.settings.download_path
        audio_quality = quality or self.settings.default_audio_quality

        console.print(f"\n[cyan]🎵 {_('Getting audio information...')}[/cyan]\n")

        try:
            info = self._extract_info(url)
            self._show_info(info)
        except Exception as e:
            console.print(f"[red]{_('Error retrieving information:')}[/red] {e}")
            return False

        msg = _('Downloading audio in format {format} ({quality}kbps)...').format(
            format=self.settings.default_audio_format, quality=audio_quality)
        console.print(f"\n[cyan]⬇️  {msg}[/cyan]\n")

        opts = self._get_audio_opts(audio_quality, output_path)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            console.print(f"\n[green]✓[/green] {_('Audio downloaded to:')} {output_path}")
            return True
        except yt_dlp.utils.DownloadError as e:
            console.print(f"\n[red]✗[/red] {_('Download error:')} {e}")
            return False
        except Exception as e:
            console.print(f"\n[red]✗[/red] {_('Unexpected error:')} {e}")
            return False

    def get_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del video/audio sin descargar."""
        try:
            info = self._extract_info(url)
            self._show_info(info)
            return info
        except Exception as e:
            console.print(f"[red]{_('Error retrieving information:')}[/red] {e}")
            return None

    def download_video(
        self,
        url: str,
        quality: Optional[str] = None,
        output: Optional[Path] = None,
    ) -> bool:
        """Descarga video de YouTube."""
        output_path = output or self.settings.download_path
        video_quality = quality or self.settings.default_video_res

        console.print(f"\n[cyan]📺 {_('Getting video information...')}[/cyan]\n")

        try:
            info = self._extract_info(url)
            self._show_info(info)
        except Exception as e:
            console.print(f"[red]{_('Error retrieving information:')}[/red] {e}")
            return False

        msg = _('Downloading video in {quality}p quality...').format(quality=video_quality)
        console.print(f"\n[cyan]⬇️  {msg}[/cyan]\n")

        opts = self._get_video_opts(video_quality, output_path)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            console.print(f"\n[green]✓[/green] {_('Video downloaded to:')} {output_path}")
            return True
        except yt_dlp.utils.DownloadError as e:
            console.print(f"\n[red]✗[/red] {_('Download error:')} {e}")
            return False
        except Exception as e:
            console.print(f"\n[red]✗[/red] {_('Unexpected error:')} {e}")
            return False
