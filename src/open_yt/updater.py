import os
import shutil
import subprocess
import sys
from typing import Tuple

from open_yt.i18n import _


def is_frozen() -> bool:
    """Retorna True si la aplicación corre como ejecutable empaquetado (PyInstaller, etc.)."""
    return getattr(sys, "frozen", False)


def is_403_error(exception: Exception) -> bool:
    """Detecta si el error corresponde a una prohibición HTTP 403 de YouTube."""
    msg = str(exception)
    return "403" in msg or "Forbidden" in msg or "HTTP Error 403" in msg


def reload_yt_dlp() -> None:
    """Recarga los módulos de yt_dlp en memoria para aplicar actualizaciones en caliente."""
    for mod in list(sys.modules.keys()):
        if mod == "yt_dlp" or mod.startswith("yt_dlp."):
            del sys.modules[mod]


def update_engine() -> Tuple[bool, str]:
    """
    Intenta actualizar yt-dlp de forma robusta según el entorno de ejecución.
    Retorna (éxito: bool, mensaje: str).
    """
    if is_frozen():
        return False, _(
            "Running as standalone executable. Please download the latest release from GitHub: "
            "https://github.com/elisbanpaco/open-yt/releases"
        )

    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    commands_to_try = []

    if in_venv:
        # Prioridad 1: Pip dentro del entorno virtual actual
        commands_to_try.append([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        if shutil.which("uv"):
            commands_to_try.append(["uv", "pip", "install", "--upgrade", "yt-dlp"])
    else:
        # Entorno no virtual (ejecución global o de usuario)
        commands_to_try.append([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "yt-dlp"])
        commands_to_try.append(
            [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--break-system-packages", "yt-dlp"]
        )
        if shutil.which("uv"):
            commands_to_try.append(["uv", "pip", "install", "--system", "--upgrade", "yt-dlp"])
        commands_to_try.append([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])

    last_error = ""
    for cmd in commands_to_try:
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90,
            )
            if res.returncode == 0:
                reload_yt_dlp()
                return True, _("Engine (yt-dlp) successfully updated.")
            else:
                last_error = (res.stderr or res.stdout or "").strip()
        except Exception as e:
            last_error = str(e)

    return False, last_error or _("Could not update yt-dlp.")
