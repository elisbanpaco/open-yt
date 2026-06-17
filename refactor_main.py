import os

file_path = "src/open_yt/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

replacements = {
    'from open_yt.ui import show_panel, show_welcome_screen, show_current_config': 'from open_yt.ui import show_panel, show_welcome_screen, show_current_config\nfrom open_yt.i18n import _',
    '"Que deseas hacer?"': '_("What do you want to do?")',
    '"Descargar Audio"': '_("Download Audio")',
    '"Descargar Video"': '_("Download Video")',
    '"Configuracion"': '_("Configuration")',
    '"Salir"': '_("Exit")',
    'choice == "Salir"': 'choice == _("Exit")',
    '"\\n[dim]Hasta luego.[/dim]"': 'f"\\n[dim]{_(\'Goodbye.\')}[/dim]"',
    'choice == "Configuracion"': 'choice == _("Configuration")',
    '"Ingresa la URL de YouTube:"': '_("Enter YouTube URL:")',
    '"Por favor ingresa una URL valida"': '_("Please enter a valid URL")',
    '"[red]URL requerida[/red]"': 'f"[red]{_(\'URL is required\')}[/red]"',
    'choice == "Descargar Audio"': 'choice == _("Download Audio")',
    '"\\n[green]✓[/green] Descarga completada"': 'f"\\n[green]✓[/green] {_(\'Download complete\')}"',
    '"\\n[red]✗[/red] La descarga fallo"': 'f"\\n[red]✗[/red] {_(\'Download failed\')}"',
    '"Deseas realizar otra accion?"': '_("Do you want to perform another action?")',
    '"Ver configuracion actual"': '_("View current configuration")',
    '"Cambiar directorio de descarga"': '_("Change download directory")',
    '"Cambiar formato de audio"': '_("Change audio format")',
    '"Cambiar calidad de audio"': '_("Change audio quality")',
    '"Cambiar formato de video"': '_("Change video format")',
    '"Cambiar resolucion de video"': '_("Change video resolution")',
    '"Alternar portada incrustada"': '_("Toggle embedded thumbnail")',
    '"Volver al menu principal"': '_("Return to main menu")',
    'choice == "Volver al menu principal"': 'choice == _("Return to main menu")',
    'choice == "Ver configuracion actual"': 'choice == _("View current configuration")',
    'choice == "Cambiar directorio de descarga"': 'choice == _("Change download directory")',
    'choice == "Cambiar formato de audio"': 'choice == _("Change audio format")',
    'choice == "Cambiar calidad de audio"': 'choice == _("Change audio quality")',
    'choice == "Cambiar formato de video"': 'choice == _("Change video format")',
    'choice == "Cambiar resolucion de video"': 'choice == _("Change video resolution")',
    'choice == "Alternar portada incrustada"': 'choice == _("Toggle embedded thumbnail")',
    'f"Nueva ruta (actual: {current_path}):"': '_("New path (current: {path}):").format(path=current_path)',
    'f"El directorio \'{new_path}\' no existe. Desea crearlo?"': '_("Directory \'{path}\' does not exist. Create it?").format(path=new_path)',
    '"[red]Directorio no creado. Configuracion sin cambios.[/red]"': 'f"[red]{_(\'Directory not created. Configuration unchanged.\')}[/red]"',
    '"[green]Configuracion actualizada y guardada.[/green]"': 'f"[green]{_(\'Configuration updated and saved.\')}[/green]"',
    '"[red]Directorio no valido.[/red]"': 'f"[red]{_(\'Invalid directory.\')}[/red]"',
    'f"Selecciona el formato de audio (actual: {settings.default_audio_format}):"': '_("Select audio format (current: {format}):").format(format=settings.default_audio_format)',
    'f"Selecciona la calidad de audio en kbps (actual: {settings.default_audio_quality}):"': '_("Select audio quality in kbps (current: {quality}):").format(quality=settings.default_audio_quality)',
    'f"Selecciona el formato de video (actual: {settings.default_video_format}):"': '_("Select video format (current: {format}):").format(format=settings.default_video_format)',
    'f"Selecciona la resolucion de video (actual: {settings.default_video_res}p):"': '_("Select video resolution (current: {res}p):").format(res=settings.default_video_res)',
    'status = "activada" if settings.embed_thumbnail else "desactivada"': 'status = _("enabled") if settings.embed_thumbnail else _("disabled")',
    'f"[green]Portada incrustada {status}.[/green]"': 'f"[green]{_(\'Embedded thumbnail\')} {status}.[/green]"'
}

for k, v in replacements.items():
    code = code.replace(k, v)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Refactor completed")
