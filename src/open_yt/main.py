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
    choice = safe_questionary(lambda: questionary.select(
        _("What do you want to do?"),
        choices=[
            _("Download Audio"),
            _("Download Video"),
            _("Configuration"),
            _("Exit"),
        ],
        qmark=">",
        style=WAVE_STYLE,
    ).ask())

    if choice == _("Exit") or choice is None:
        console.print(f"\n[dim]{_('Goodbye.')}[/dim]")
        return

    if choice == _("Configuration"):
        config_menu()
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

    downloader = MediaDownloader()

    if choice == _("Download Audio"):
        success = downloader.download_audio(url)
    else:
        success = downloader.download_video(url)

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
    """Menu interactivo de configuracion."""
    while True:
        choice = safe_questionary(lambda: questionary.select(
            _("Configuration"),
            choices=[
                _("View current configuration"),
                _("Change download directory"),
                _("Change audio format"),
                _("Change audio quality"),
                _("Change video format"),
                _("Change video resolution"),
                _("Toggle embedded thumbnail"),
                _("Return to main menu"),
            ],
            qmark=">",
            style=WAVE_STYLE,
        ).ask())

        if choice == _("Return to main menu") or choice is None:
            return

        if choice == _("View current configuration"):
            config_show()
            continue

        if choice == _("Change download directory"):
            settings = get_settings()
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
                        console.print(f"[red]{_('Directory not created. Configuration unchanged.')}[/red]")
                        continue
                
                if path.exists():
                    settings.download_path = path
                    settings.save()
                    reload_settings()
                    console.print(f"[green]{_('Configuration updated and saved.')}[/green]")
                else:
                    console.print(f"[red]{_('Invalid directory.')}[/red]")
            continue

        if choice == _("Change audio format"):
            settings = get_settings()
            new_format = safe_questionary(lambda: questionary.select(
                _("Select audio format (current: {format}):").format(format=settings.default_audio_format),
                choices=["mp3", "m4a", "wav", "flac"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_format:
                settings.default_audio_format = new_format
                settings.save()
                reload_settings()
                console.print(f"[green]{_('Configuration updated and saved.')}[/green]")
            continue

        if choice == _("Change audio quality"):
            settings = get_settings()
            new_quality = safe_questionary(lambda: questionary.select(
                _("Select audio quality in kbps (current: {quality}):").format(quality=settings.default_audio_quality),
                choices=["320", "256", "192", "128"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_quality:
                settings.default_audio_quality = new_quality
                settings.save()
                reload_settings()
                console.print(f"[green]{_('Configuration updated and saved.')}[/green]")
            continue

        if choice == _("Change video format"):
            settings = get_settings()
            new_format = safe_questionary(lambda: questionary.select(
                _("Select video format (current: {format}):").format(format=settings.default_video_format),
                choices=["mp4", "mkv", "webm"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_format:
                settings.default_video_format = new_format
                settings.save()
                reload_settings()
                console.print(f"[green]{_('Configuration updated and saved.')}[/green]")
            continue

        if choice == _("Change video resolution"):
            settings = get_settings()
            new_res = safe_questionary(lambda: questionary.select(
                _("Select video resolution (current: {res}p):").format(res=settings.default_video_res),
                choices=["2160", "1080", "720", "480", "360"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_res:
                settings.default_video_res = new_res
                settings.save()
                reload_settings()
                console.print(f"[green]{_('Configuration updated and saved.')}[/green]")
            continue

        if choice == _("Toggle embedded thumbnail"):
            settings = get_settings()
            settings.embed_thumbnail = not settings.embed_thumbnail
            settings.save()
            reload_settings()
            status = _("enabled") if settings.embed_thumbnail else _("disabled")
            console.print(f"[green]{_('Embedded thumbnail')} {status}.[/green]")
            continue


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
