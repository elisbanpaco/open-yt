from pathlib import Path
from typing import Any, Dict, Optional

import yt_dlp

from open_yt.config import Settings
from open_yt.i18n import _
from open_yt.ui import ProgressHook, console, show_media_info, get_status_spinner
from open_yt.updater import is_403_error, is_frozen, update_engine
from open_yt.symbols import Symbols


class SilentLogger:
    """Silencia los logs crudos de yt-dlp para manejar los errores nosotros mismos."""
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class MediaDownloader:
    """Clase principal para la descarga de media usando yt-dlp."""

    def __init__(self) -> None:
        """Inicializa el descargador con la configuración."""
        self.settings = Settings.load()
        self._ydl_opts: Dict[str, Any] = {}
        self._logger = SilentLogger()

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
            "logger": self._logger,
        }

    def _get_video_opts(self, quality: str, output_path: Path) -> Dict[str, Any]:
        """Genera opciones de yt-dlp para descarga de video."""
        format_str = f"bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "best"
        
        postprocessors = []
        if self.settings.embed_thumbnail:
            postprocessors.append({"key": "EmbedThumbnail"})
            
        opts = {
            "format": format_str,
            "merge_output_format": self.settings.default_video_format,
            "outtmpl": str(output_path / "%(title)s.%(ext)s"),
            "progress_hooks": [ProgressHook()],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "logger": self._logger,
        }
        
        if self.settings.embed_thumbnail:
            opts["writethumbnail"] = True
            opts["postprocessors"] = postprocessors
            
        return opts

    def _extract_info(self, url: str, _retried: bool = False) -> Dict[str, Any]:
        """Extrae metadatos del video sin descargar."""
        opts: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "noplaylist": True,
            "logger": self._logger,
        }
        with get_status_spinner(_("Extracting metadata...")):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info is None:
                        raise ValueError(_("Could not retrieve video information"))
                    return info
            except Exception as e:
                if is_403_error(e) and not _retried:
                    console.print(f"\n[yellow]{Symbols.WARNING} {_('YouTube blocked metadata extraction (HTTP 403 Forbidden). Engine might be outdated.')}[/yellow]")
                    if not is_frozen():
                        console.print(f"[cyan]{Symbols.RETRY} {_('Attempting automatic engine update (yt-dlp)...')}[/cyan]")
                        success, update_msg = update_engine()
                        if success:
                            console.print(f"[green]{Symbols.SUCCESS} {_('Engine successfully updated! Retrying metadata extraction...')}[/green]\n")
                            return self._extract_info(url, _retried=True)
                raise

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
        _retried: bool = False,
    ) -> bool:
        """Descarga audio de YouTube."""
        output_path = output or self.settings.download_path
        audio_quality = quality or self.settings.default_audio_quality

        console.print(f"\n[cyan]{Symbols.AUDIO} {_('Getting audio information...')}[/cyan]\n")

        try:
            info = self._extract_info(url)
            self._show_info(info)
        except Exception as e:
            console.print(f"[red]{_('Error retrieving information:')}[/red] {e}")
            return False

        msg = _('Downloading audio in format {format} ({quality}kbps)...').format(
            format=self.settings.default_audio_format, quality=audio_quality)
        console.print(f"\n[cyan]{Symbols.DOWNLOAD} {msg}[/cyan]\n")

        opts = self._get_audio_opts(audio_quality, output_path)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            console.print(f"\n[green]{Symbols.SUCCESS}[/green] {_('Audio downloaded to:')} {output_path}")
            return True
        except yt_dlp.utils.DownloadError as e:
            if is_403_error(e) and not _retried:
                console.print(f"\n[yellow]{Symbols.WARNING} {_('YouTube blocked the download (HTTP 403 Forbidden). Engine might be outdated.')}[/yellow]")
                if is_frozen():
                    console.print(f"[dim]{_('Running as standalone binary. Please download the latest release from GitHub.')}[/dim]\n")
                else:
                    console.print(f"[cyan]{Symbols.RETRY} {_('Attempting automatic engine update (yt-dlp)...')}[/cyan]")
                    success, msg = update_engine()
                    if success:
                        console.print(f"[green]{Symbols.SUCCESS} {_('Engine successfully updated! Retrying download...')}[/green]\n")
                        return self.download_audio(url, quality=quality, output=output, _retried=True)
                    else:
                        console.print(f"[dim]{_('Automatic update could not proceed:')} {msg}[/dim]\n")
            console.print(f"\n[red]{Symbols.ERROR}[/red] {_('Download error:')} {e}")
            return False
        except Exception as e:
            console.print(f"\n[red]{Symbols.ERROR}[/red] {_('Unexpected error:')} {e}")
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
        _retried: bool = False,
    ) -> bool:
        """Descarga video de YouTube."""
        output_path = output or self.settings.download_path
        video_quality = quality or self.settings.default_video_res

        console.print(f"\n[cyan]{Symbols.VIDEO} {_('Getting video information...')}[/cyan]\n")

        try:
            info = self._extract_info(url)
            self._show_info(info)
        except Exception as e:
            console.print(f"[red]{_('Error retrieving information:')}[/red] {e}")
            return False

        msg = _('Downloading video in {quality}p quality...').format(quality=video_quality)
        console.print(f"\n[cyan]{Symbols.DOWNLOAD} {msg}[/cyan]\n")

        opts = self._get_video_opts(video_quality, output_path)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            console.print(f"\n[green]{Symbols.SUCCESS}[/green] {_('Video downloaded to:')} {output_path}")
            return True
        except yt_dlp.utils.DownloadError as e:
            if is_403_error(e) and not _retried:
                console.print(f"\n[yellow]{Symbols.WARNING} {_('YouTube blocked the download (HTTP 403 Forbidden). Engine might be outdated.')}[/yellow]")
                if is_frozen():
                    console.print(f"[dim]{_('Running as standalone binary. Please download the latest release from GitHub.')}[/dim]\n")
                else:
                    console.print(f"[cyan]{Symbols.RETRY} {_('Attempting automatic engine update (yt-dlp)...')}[/cyan]")
                    success, msg = update_engine()
                    if success:
                        console.print(f"[green]{Symbols.SUCCESS} {_('Engine successfully updated! Retrying download...')}[/green]\n")
                        return self.download_video(url, quality=quality, output=output, _retried=True)
                    else:
                        console.print(f"[dim]{_('Automatic update could not proceed:')} {msg}[/dim]\n")
            console.print(f"\n[red]{Symbols.ERROR}[/red] {_('Download error:')} {e}")
            return False
        except Exception as e:
            console.print(f"\n[red]{Symbols.ERROR}[/red] {_('Unexpected error:')} {e}")
            return False
