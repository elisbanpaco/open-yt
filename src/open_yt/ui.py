from typing import Any, Dict, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


console = Console()


_C1    = "#8B1538"        # rojo oscuro profundo (inicio del gradiente)
_C2    = "#C4374B"        # rojo medio vibrante
_C3    = "#E56B6F"        # coral/rosa medio
_C4    = "#F4A382"        # salmón/naranja claro (fin del gradiente)
_DIM   = "grey50"         # separadores y texto secundario
_LABEL = "misty_rose3"    # etiquetas (rosado neutro, no compite con el rojo)
_OK    = "dark_sea_green3" # éxito (verde apagado, no chilla junto al rojo)
_ERR   = "bright_red"     # error (único rojo puro, solo para errores reales)


_LOGO_ROWS = [
    (_C1,  "  ██████╗ ██████╗ ███████╗███╗   ██╗",  _C1, "██╗   ██╗████████╗"),
    (_C1,  " ██╔═══██╗██╔══██╗██╔════╝████╗  ██║",  _C1, "╚██╗ ██╔╝╚══██╔══╝"),
    (_C2,  " ██║   ██║██████╔╝█████╗  ██╔██╗ ██║",  _C2, "  ╚████╔╝    ██║   "),
    (_C2,  " ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║",  _C2, "   ╚██╔╝     ██║   "),
    (_C3,  " ╚██████╔╝██║     ███████╗██║ ╚████║",  _C3, "   ██║      ██║   "),
    (_C4,  "  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝",  _C4, "   ╚═╝      ╚═╝   "),
]
_SEP_LEFT  = "  █████╗  " 
_SEP_RIGHT = "  ╚════╝  "


def _build_logo() -> Text:
    """Construye el logo con gradiente usando Rich Text."""
    logo = Text(justify="center")
    for i, (lc, left, rc, right) in enumerate(_LOGO_ROWS):
        # separador central solo en filas 2 y 3 (índice 2 y 3)
        mid = ""
        mid_style = _DIM
        if i == 2:
            mid = " █████╗  "
        elif i == 3:
            mid = " ╚════╝  "

        logo.append(left, style=f"bold {lc}")
        if mid:
            logo.append(mid, style=f"dim {mid_style}")
        else:
            logo.append("          ")
        logo.append(right, style=f"bold {rc}")
        logo.append("\n")
    return logo


def show_welcome_screen() -> None:
    """Pantalla de bienvenida """
    console.clear()

    # Logo
    console.print()
    console.print(_build_logo())

    console.print(Rule(style=_DIM), width=68)

    meta = Text(justify="center")
    meta.append("v0.1.1.5", style=f"bold {_C2}")
    meta.append("  ·  ", style=_DIM)
    meta.append("Open Source Media Engine", style=_DIM)
    console.print(meta)

    console.print(Rule(style=_DIM), width=68)
    console.print()

def format_duration(seconds: Optional[int]) -> str:
    if seconds is None:
        seconds = 0
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def format_number(num: Optional[int]) -> str:
    if num is None:
        num = 0
    return f"{num:,}"


def show_media_card(info_dict: Dict[str, Any]) -> None:
    """Tarjeta de metadatos con paleta naranja-dorada."""
    title = info_dict.get("title") or "Unknown"
    duration = format_duration(info_dict.get("duration") or 0)
    channel = info_dict.get("uploader") or info_dict.get("channel") or "Unknown"
    views = format_number(info_dict.get("view_count") or 0)
    likes = format_number(info_dict.get("like_count") or 0)
    upload_date = info_dict.get("upload_date") or "Unknown"

    tbl = Table(box=None, show_header=False, padding=(0, 1))
    tbl.add_column("Label", style=_LABEL, width=14)
    tbl.add_column("Value", style="white")

    tbl.add_row("Titulo:",     title)
    tbl.add_row("Canal:",      channel)
    tbl.add_row("Duracion:",   duration)
    tbl.add_row("Vistas:",     views)
    tbl.add_row("Likes:",      likes)
    tbl.add_row("Fecha:",      upload_date)

    if info_dict.get("resolution") and info_dict.get("resolution") != "N/A":
        tbl.add_row("Resolucion:", info_dict["resolution"])

    console.print(
        Panel(
            tbl,
            box=box.ROUNDED,
            border_style=_DIM,
            padding=(1, 2),
            width=75,
            title=f"[{_C2}]Información[/{_C2}]",
            title_align="left",
        )
    )


def show_current_config(config_dict: Dict[str, Any]) -> None:
    """Panel de configuración con secciones y paleta coherente."""
    download_path  = str(config_dict.get("download_path",         "N/A"))
    audio_format   = config_dict.get("default_audio_format",      "N/A")
    audio_quality  = config_dict.get("default_audio_quality",     "N/A")
    video_format   = config_dict.get("default_video_format",      "N/A")
    video_res      = config_dict.get("default_video_res",         "N/A")

    content = Text()
    content.append("Rutas\n",                                  style=f"bold {_C2}")
    content.append(f"  Directorio: {download_path}\n\n",       style="white")
    content.append("Audio\n",                                  style=f"bold {_C2}")
    content.append(
        f"  Formato: {audio_format}  |  Calidad: {audio_quality} kbps\n\n",
        style="white",
    )
    content.append("Video\n",                                  style=f"bold {_C2}")
    content.append(
        f"  Formato: {video_format}  |  Resolución: {video_res}p\n\n",
        style="white",
    )
    content.append("Extras\n",                                 style=f"bold {_C2}")
    embed_thumb = config_dict.get("embed_thumbnail", True)
    thumb_status = "Activada" if embed_thumb else "Desactivada"
    content.append(
        f"  Portada incrustada: {thumb_status}",
        style="white",
    )

    console.print(
        Panel(
            content,
            box=box.ROUNDED,
            border_style=_DIM,
            padding=(1, 2),
            width=75,
            title=f"[{_C2}]Configuración[/{_C2}]",
            title_align="left",
        )
    )


# Alias de compatibilidad
def show_media_info(info_dict: Dict[str, Any]) -> None:
    show_media_card(info_dict)


class ProgressHook:
    """Hook de progreso para yt-dlp compatible con Rich."""

    def __init__(
        self,
        description: str = "Descargando",
        bar_style: str = _C2, 
        text_style: str = "white",
    ) -> None:
        self.description = description
        self.bar_style   = bar_style
        self.text_style  = text_style
        self._progress: Optional[Progress] = None
        self._task_id:  Optional[int]      = None

    def __call__(self, d: Dict[str, Any]) -> None:
        status = d.get("status")
        if   status == "starting":     self._handle_starting(d)
        elif status == "downloading":  self._handle_downloading(d)
        elif status == "finished":     self._handle_finished(d)
        elif status == "error":        self._handle_error(d)

    def _init_progress(self, total: float, title: str) -> None:
        if self._progress is not None:
            return
        self._progress = Progress(
            TextColumn(
                f"[{self.text_style}]{self.description}: {{task.description}}",
            ),
            BarColumn(bar_width=40, style=self.bar_style, complete_style=_C3),
            TextColumn(
                f"[{_C4}]{{task.percentage:>3.0f}}%",
            ),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(title, total=total)

    def _handle_starting(self, d: Dict[str, Any]) -> None:
        total    = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        filename = d.get("filename", "Archivo")
        self._init_progress(total, filename)

    def _handle_downloading(self, d: Dict[str, Any]) -> None:
        if self._progress is None or self._task_id is None:
            total    = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            filename = d.get("filename", "Archivo")
            self._init_progress(total, filename)

        downloaded = d.get("downloaded_bytes", 0)
        total      = d.get("total_bytes") or d.get("total_bytes_estimate", 1)

        if self._progress and self._task_id is not None:
            self._progress.update(self._task_id, completed=downloaded, total=total)

    def _handle_finished(self, d: Dict[str, Any]) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._task_id  = None
        console.print(
            f"[{_OK}]✓[/{_OK}] [white]Descarga completada:[/white] "
            f"[{_C2}]{d.get('filename', '')}[/{_C2}]"
        )

    def _handle_error(self, d: Dict[str, Any]) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._task_id  = None
        console.print(
            f"[{_ERR}]✗[/{_ERR}] [white]Error:[/white] "
            f"[{_ERR}]{d.get('error', 'Error desconocido')}[/{_ERR}]"
        )


def show_panel(
    title: str,
    content: str,
    style: str = _C2,
    expand: bool = True,
) -> None:
    console.print(
        Panel(content, title=title, border_style=_DIM, expand=expand)
    )


def get_status_spinner(message: str):
    return console.status(
        f"[{_C2}]{message}[/{_C2}]",
        spinner="dots",
        spinner_style=_C2,
    )