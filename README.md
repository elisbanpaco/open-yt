# OPEN-YT 🟥

> The high-performance, minimalist open-source YouTube engine for audio and video.

[![PyPI version](https://img.shields.io/pypi/v/open-yt.svg)](https://pypi.org/project/open-yt/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

![OPEN-YT Demo](assets/open-yt-demo.gif)

OPEN-YT es una Interfaz de Línea de Comandos (CLI) de grado industrial diseñada para extraer audio y video con la máxima eficiencia. Combina la potencia de `yt-dlp` con una experiencia de usuario (UX) minimalista, elegante y altamente configurable.

## ✨ Características

* **UI/UX:** Interfaz de terminal renderizada con `Rich` y menús interactivos fluidos potenciados por `Questionary`.
* **Modo Rápido (Fast Path):** Opciones para evitar menús y descargar contenido en un segundo usando solo la URL.
* **Motor Asíncrono:** Descargas ultra rápidas y extracción de metadatos sin bloquear la interfaz.
* **Mantenimiento Autónomo:** Comando `update` integrado para evadir bloqueos de YouTube actualizando el motor automáticamente.
* **Persistencia de Estado:** Recuerda tus preferencias de formato (MP3, FLAC, MP4, MKV), resolución y rutas de descarga localmente.
* **Instalación Global Directa:** Distribuido a través de PyPI. Se instala como un comando de sistema disponible desde cualquier terminal.

---


## 🚀 Instalación

### Opción 1: Descargar el Ejecutable (No requiere Python)
Si no eres programador, ve a la pestaña de **[Releases](../../releases)** en GitHub y descarga la última versión para Windows, Mac o Linux. ¡Solo dale doble clic y úsalo!

### Opción 2: Usando `uv` o `pip` (Recomendado para Devs)
Puedes instalar OPEN-YT globalmente en tu sistema:

Usando **uv** (Más rápido):
```bash
uv tool install open-yt
```

Usando **pip** (Tradicional):
```bash
pip install open-yt
```

---

## ⚡ Uso

**Modo Interactivo (Menús UI):**
Simplemente abre la terminal y escribe el nombre del programa:
```bash
open-yt
```

**Modo Rápido (Para Expertos):**
Pega el enlace directamente para saltarte los menús:
```bash
open-yt https://youtu.be/xxx       # Descarga un video (con tus opciones por defecto)
open-yt https://youtu.be/xxx -a    # Fuerza la descarga en audio (MP3)
```

**Mantenimiento:**
Si YouTube cambia sus reglas y las descargas fallan, actualiza el motor:
```bash
open-yt update
```

---

## 💻 Instalación para Desarrolladores

Si deseas explorar el código fuente, modificar la herramienta o compilarla tú mismo:

```bash
# 1. Clonar el repositorio
git clone https://github.com/elisbanpaco/open-yt.git
cd open-yt

# 2. Crear el entorno virtual e instalar dependencias
uv sync

# 3. Ejecutar
uv run open-yt