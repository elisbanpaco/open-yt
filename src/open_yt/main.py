import os
import sys
import typer
from pathlib import Path
from typing import Any, Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.table import Table

from open_yt.config import Settings, get_settings, reload_settings
from open_yt.downloader import MediaDownloader
from open_yt.ui import show_panel, show_welcome_screen, show_current_config
from open_yt.i18n import _

app = typer.Typer(
    name="wolfcode",
    help="CLI profesional para descargar contenido de YouTube",
    add_completion=False,
)
console = Console()

video_app = typer.Typer(help="Descargar videos de YouTube")
audio_app = typer.Typer(help="Descargar audio de YouTube")
config_app = typer.Typer(help="Gestionar configuración")

app.add_typer(video_app, name="video")
app.add_typer(audio_app, name="audio")
app.add_typer(config_app, name="config")

WAVE_STYLE = Style([
    ("qmark", "fg:cyan bold"),
    ("pointer", "fg:cyan bold"),
    ("selected", "fg:cyan bold"),
    ("separator", "fg:cyan"),
    ("question", "bold #ffffff"),
    ("answer", "fg:cyan bold"),
])


def safe_questionary(prompt_func) -> Optional[Any]:
    """Envuelve questionary para manejo elegante de excepciones."""
    try:
        return prompt_func()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Sesion finalizada.[/dim]")
        sys.exit(0)
    except Exception:
        console.print("\n[dim]Sesion finalizada.[/dim]")
        sys.exit(0)


def run_interactive_menu() -> None:
    """Ejecuta el menú interactivo con questionary."""
    action = safe_questionary(lambda: questionary.select(
        _("What do you want to do?"),
        choices=[
            _("Download from URL"),
            _("Configuration"),
            _("Exit"),
        ],
        qmark=">",
        style=WAVE_STYLE,
    ).ask())

    if action == _("Exit") or action is None:
        console.print(f"\n[dim]{_('Goodbye.')}[/dim]")
        return

    if action == _("Configuration"):
        config_menu()
        console.clear()
        show_welcome_screen()
        run_interactive_menu()
        return

    url = safe_questionary(lambda: questionary.text(
        _("Enter YouTube URL:"),
        qmark=">",
        style=WAVE_STYLE,
        validate=lambda x: len(x) > 0 or _("Please enter a valid URL"),
    ).ask())

    if not url:
        console.print(f"[red]{_('URL is required')}[/red]")
        run_interactive_menu()
        return

    console.clear()
    show_welcome_screen()
    downloader = MediaDownloader()
    
    # El CLI extrae información y automáticamente muestra la tarjeta (Media Card)
    info = downloader.get_info(url)
    if not info:
        run_interactive_menu()
        return
    
    settings = get_settings()

    choice = safe_questionary(lambda: questionary.select(
        _("What do you want to extract?"),
        choices=[
            _("Quick Audio Download ({format} {quality}kbps)").format(format=settings.default_audio_format.upper(), quality=settings.default_audio_quality),
            _("Quick Video Download ({res}p)").format(res=settings.default_video_res),
            _("Custom Audio Download..."),
            _("Custom Video Download..."),
            _("Cancel"),
        ],
        qmark=">",
        style=WAVE_STYLE,
    ).ask())

    if not choice or choice == _("Cancel"):
        console.clear()
        show_welcome_screen()
        run_interactive_menu()
        return

    success = False
    if choice.startswith(_("Quick Audio")):
        success = downloader.download_audio(url)
    elif choice.startswith(_("Quick Video")):
        success = downloader.download_video(url)
    elif choice == _("Custom Audio Download..."):
        format_choice = safe_questionary(lambda: questionary.select(
            _("Select audio format:"), choices=["mp3", "m4a", "wav", "flac"], style=WAVE_STYLE).ask())
        quality_choice = safe_questionary(lambda: questionary.select(
            _("Select quality (kbps):"), choices=["320", "256", "192", "128"], style=WAVE_STYLE).ask())
        if format_choice and quality_choice:
            # Override settings temporarily
            old_fmt = settings.default_audio_format
            old_q = settings.default_audio_quality
            settings.default_audio_format = format_choice
            settings.default_audio_quality = quality_choice
            success = downloader.download_audio(url, quality=quality_choice)
            settings.default_audio_format = old_fmt
            settings.default_audio_quality = old_q
    elif choice == _("Custom Video Download..."):
        res_choice = safe_questionary(lambda: questionary.select(
            _("Select video resolution:"), choices=["2160", "1080", "720", "480", "360"], style=WAVE_STYLE).ask())
        if res_choice:
            success = downloader.download_video(url, quality=res_choice)

    if success:
        console.print(f"\n[green]✓[/green] {_('Download complete')}")
    else:
        console.print(f"\n[red]✗[/red] {_('Download failed')}")

    continue_choice = safe_questionary(lambda: questionary.confirm(
        _("Do you want to perform another action?"),
        default=True,
        style=WAVE_STYLE,
    ).ask())

    if continue_choice:
        console.clear()
        show_welcome_screen()
        run_interactive_menu()
    else:
        console.print(f"\n[dim]{_('Goodbye.')}[/dim]")


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
) -> None:
    """Callback principal que detecta si no hay argumentos."""
    if ctx.invoked_subcommand is None:
        show_welcome_screen()
        run_interactive_menu()


@video_app.command("download")
def video_download(
    url: str = typer.Argument(..., help="URL del video de YouTube"),
    quality: str = typer.Option("best", "--quality", "-q", help="Calidad del video (best, 1080p, 720p, etc.)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Directorio de salida"),
):
    """Descargar video de YouTube"""
    output_path = Path(output) if output else None
    downloader = MediaDownloader()

    success = downloader.download_video(url, quality=quality, output=output_path)

    if not success:
        raise typer.Exit(1)


@video_app.command("info")
def video_info(
    url: str = typer.Argument(..., help="URL del video de YouTube"),
):
    """Mostrar información del video sin descargar"""
    downloader = MediaDownloader()
    success = downloader.get_info(url)
    if not success:
        raise typer.Exit(1)


@audio_app.command("download")
def audio_download(
    url: str = typer.Argument(..., help="URL del video/playlist de YouTube"),
    format: str = typer.Option("mp3", "--format", "-f", help="Formato de audio (mp3, flac, wav, etc.)"),
    quality: str = typer.Option("320", "--quality", "-q", help="Calidad del audio (320, 256, 128 kbps)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Directorio de salida"),
    playlist: bool = typer.Option(False, "--playlist", "-p", help="Descargar playlist completa"),
):
    """Descargar audio de YouTube"""
    output_path = Path(output) if output else None
    downloader = MediaDownloader()

    success = downloader.download_audio(url, quality=quality, output=output_path)

    if not success:
        raise typer.Exit(1)


@audio_app.command("info")
def audio_info(
    url: str = typer.Argument(..., help="URL del video de YouTube"),
):
    """Mostrar información del audio sin descargar"""
    downloader = MediaDownloader()
    success = downloader.get_info(url)
    if not success:
        raise typer.Exit(1)


@config_app.command("show")
def config_show():
    """Mostrar configuración actual"""
    settings = get_settings()
    config_dict = {
        "download_path": settings.download_path,
        "default_audio_format": settings.default_audio_format,
        "default_audio_quality": settings.default_audio_quality,
        "default_video_format": settings.default_video_format,
        "default_video_res": settings.default_video_res,
        "embed_thumbnail": settings.embed_thumbnail,
    }
    show_current_config(config_dict)


def config_menu() -> None:
    """Menu interactivo de configuracion dinámica."""
    while True:
        console.clear()
        show_welcome_screen()
        settings = get_settings()
        
        # Opciones dinámicas con sus valores actuales
        opt_path = f"[Ruta]  {_('Download directory')}  ({settings.download_path})"
        opt_afmt = f"[Audio] {_('Default format')}      ({settings.default_audio_format})"
        opt_aql  = f"[Audio] {_('Default quality')}     ({settings.default_audio_quality} kbps)"
        opt_vfmt = f"[Video] {_('Default format')}      ({settings.default_video_format})"
        opt_vres = f"[Video] {_('Default resolution')}  ({settings.default_video_res}p)"
        thumb_st = _("enabled") if settings.embed_thumbnail else _("disabled")
        opt_thmb = f"[Extra] {_('Embedded thumbnail')}  ({thumb_st})"
        opt_back = _("Return to main menu")

        choice = safe_questionary(lambda: questionary.select(
            _("Configuration (Select to edit)"),
            choices=[
                opt_path,
                opt_afmt,
                opt_aql,
                opt_vfmt,
                opt_vres,
                opt_thmb,
                questionary.Separator("────────────────────────────────────────"),
                opt_back,
            ],
            qmark=">",
            style=WAVE_STYLE,
        ).ask())

        if choice == opt_back or choice is None:
            return

        if choice == opt_path:
            current_path = str(settings.download_path)
            new_path = safe_questionary(lambda: questionary.path(
                _("New path (current: {path}):").format(path=current_path),
                default=current_path,
                only_directories=True,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_path and new_path != current_path:
                path = Path(new_path)
                if not path.exists():
                    create = safe_questionary(lambda: questionary.confirm(
                        _("Directory '{path}' does not exist. Create it?").format(path=new_path),
                        default=True,
                        style=WAVE_STYLE,
                    ).ask())
                    if create:
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        continue
                if path.exists():
                    settings.download_path = path
                    settings.save()
                    reload_settings()

        elif choice == opt_afmt:
            new_format = safe_questionary(lambda: questionary.select(
                _("Select audio format:"),
                choices=["mp3", "m4a", "wav", "flac"],
                default=settings.default_audio_format,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())
            if new_format:
                settings.default_audio_format = new_format
                settings.save()
                reload_settings()

        elif choice == opt_aql:
            new_quality = safe_questionary(lambda: questionary.select(
                _("Select audio quality in kbps:"),
                choices=["320", "256", "192", "128"],
                default=settings.default_audio_quality,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())
            if new_quality:
                settings.default_audio_quality = new_quality
                settings.save()
                reload_settings()

        elif choice == opt_vfmt:
            new_format = safe_questionary(lambda: questionary.select(
                _("Select video format:"),
                choices=["mp4", "mkv", "webm"],
                default=settings.default_video_format,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())
            if new_format:
                settings.default_video_format = new_format
                settings.save()
                reload_settings()

        elif choice == opt_vres:
            new_res = safe_questionary(lambda: questionary.select(
                _("Select video resolution:"),
                choices=["2160", "1080", "720", "480", "360"],
                default=settings.default_video_res,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())
            if new_res:
                settings.default_video_res = new_res
                settings.save()
                reload_settings()

        elif choice == opt_thmb:
            settings.embed_thumbnail = not settings.embed_thumbnail
            settings.save()
            reload_settings()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Clave de configuracion a modificar"),
    value: str = typer.Argument(..., help="Nuevo valor"),
):
    """Modificar configuracion"""
    settings = Settings.load()

    if key == "download_path":
        settings.download_path = Path(value)
    elif key == "default_audio_format":
        settings.default_audio_format = value
    elif key == "default_video_res":
        settings.default_video_res = value
    elif key == "default_audio_quality":
        settings.default_audio_quality = value
    elif key == "default_video_format":
        settings.default_video_format = value
    elif key == "embed_thumbnail":
        settings.embed_thumbnail = value.lower() in ("true", "1", "yes")
    else:
        console.print(f"[red]Clave desconocida:[/red] {key}")
        return

    settings.save()
    console.print(f"[green]Configuracion actualizada:[/green] {key} = {value}")


@config_app.command("reset")
def config_reset(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar reset sin preguntar"),
):
    """Restablecer configuración por defecto"""
    if confirm:
        settings = Settings()
        settings.save()
        console.print("[yellow]✓[/yellow] Configuración restablecida a valores por defecto")
    else:
        console.print("[red]Usa --yes para confirmar el reset[/red]")


@app.command()
def version():
    """Mostrar version de la aplicacion"""
    console.print("[cyan bold]WOLFCODE v1.0.0[/cyan bold]")


if __name__ == "__main__":
    app()
