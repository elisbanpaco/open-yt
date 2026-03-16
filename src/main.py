import os
import sys
import typer
from pathlib import Path
from typing import Any, Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.table import Table

from config import Settings, get_settings, reload_settings
from downloader import MediaDownloader
from ui import show_panel, show_welcome_screen, show_current_config

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
        "Que deseas hacer?",
        choices=[
            "Descargar Audio",
            "Descargar Video",
            "Configuracion",
            "Salir",
        ],
        qmark=">",
        style=WAVE_STYLE,
    ).ask())

    if choice == "Salir" or choice is None:
        console.print("\n[dim]Hasta luego.[/dim]")
        return

    if choice == "Configuracion":
        config_menu()
        run_interactive_menu()
        return

    url = safe_questionary(lambda: questionary.text(
        "Ingresa la URL de YouTube:",
        qmark=">",
        style=WAVE_STYLE,
        validate=lambda x: len(x) > 0 or "Por favor ingresa una URL valida",
    ).ask())

    if not url:
        console.print("[red]URL requerida[/red]")
        run_interactive_menu()
        return

    downloader = MediaDownloader()

    if choice == "Descargar Audio":
        success = downloader.download_audio(url)
    else:
        success = downloader.download_video(url)

    if success:
        console.print("\n[green]✓[/green] Descarga completada")
    else:
        console.print("\n[red]✗[/red] La descarga fallo")

    continue_choice = safe_questionary(lambda: questionary.confirm(
        "Deseas realizar otra accion?",
        default=True,
        style=WAVE_STYLE,
    ).ask())

    if continue_choice:
        run_interactive_menu()
    else:
        console.print("\n[dim]Hasta luego.[/dim]")


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
    }
    show_current_config(config_dict)


def config_menu() -> None:
    """Menu interactivo de configuracion."""
    while True:
        choice = safe_questionary(lambda: questionary.select(
            "Configuracion",
            choices=[
                "Ver configuracion actual",
                "Cambiar directorio de descarga",
                "Cambiar formato de audio",
                "Cambiar calidad de audio",
                "Cambiar formato de video",
                "Cambiar resolucion de video",
                "Volver al menu principal",
            ],
            qmark=">",
            style=WAVE_STYLE,
        ).ask())

        if choice == "Volver al menu principal" or choice is None:
            return

        if choice == "Ver configuracion actual":
            config_show()
            continue

        if choice == "Cambiar directorio de descarga":
            settings = get_settings()
            current_path = str(settings.download_path)
            new_path = safe_questionary(lambda: questionary.path(
                f"Nueva ruta (actual: {current_path}):",
                default=current_path,
                only_directories=True,
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_path and new_path != current_path:
                path = Path(new_path)
                if not path.exists():
                    create = safe_questionary(lambda: questionary.confirm(
                        f"El directorio '{new_path}' no existe. Desea crearlo?",
                        default=True,
                        style=WAVE_STYLE,
                    ).ask())
                    if create:
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        console.print("[red]Directorio no creado. Configuracion sin cambios.[/red]")
                        continue
                
                if path.exists():
                    settings.download_path = path
                    settings.save()
                    reload_settings()
                    console.print("[green]Configuracion actualizada y guardada.[/green]")
                else:
                    console.print("[red]Directorio no valido.[/red]")
            continue

        if choice == "Cambiar formato de audio":
            settings = get_settings()
            new_format = safe_questionary(lambda: questionary.select(
                f"Selecciona el formato de audio (actual: {settings.default_audio_format}):",
                choices=["mp3", "m4a", "wav", "flac"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_format:
                settings.default_audio_format = new_format
                settings.save()
                reload_settings()
                console.print("[green]Configuracion actualizada y guardada.[/green]")
            continue

        if choice == "Cambiar calidad de audio":
            settings = get_settings()
            new_quality = safe_questionary(lambda: questionary.select(
                f"Selecciona la calidad de audio en kbps (actual: {settings.default_audio_quality}):",
                choices=["320", "256", "192", "128"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_quality:
                settings.default_audio_quality = new_quality
                settings.save()
                reload_settings()
                console.print("[green]Configuracion actualizada y guardada.[/green]")
            continue

        if choice == "Cambiar formato de video":
            settings = get_settings()
            new_format = safe_questionary(lambda: questionary.select(
                f"Selecciona el formato de video (actual: {settings.default_video_format}):",
                choices=["mp4", "mkv", "webm"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_format:
                settings.default_video_format = new_format
                settings.save()
                reload_settings()
                console.print("[green]Configuracion actualizada y guardada.[/green]")
            continue

        if choice == "Cambiar resolucion de video":
            settings = get_settings()
            new_res = safe_questionary(lambda: questionary.select(
                f"Selecciona la resolucion de video (actual: {settings.default_video_res}p):",
                choices=["2160", "1080", "720", "480", "360"],
                qmark=">",
                style=WAVE_STYLE,
            ).ask())

            if new_res:
                settings.default_video_res = new_res
                settings.save()
                reload_settings()
                console.print("[green]Configuracion actualizada y guardada.[/green]")
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
