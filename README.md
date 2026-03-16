# WOLFCODE 🐺

> The high-performance, minimalist YouTube engine for audio and video.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build: Nuitka](https://img.shields.io/badge/Build-Nuitka-orange.svg)](https://nuitka.net/)

![WOLFCODE Demo](assets/demo.gif)
*(Nota: Aquí subiremos el GIF de la terminal en acción)*

WOLFCODE es una Interfaz de Línea de Comandos (CLI) de grado industrial diseñada para extraer audio y video con la máxima eficiencia. Combina la potencia de `yt-dlp` con una experiencia de usuario (UX) minimalista, elegante y altamente configurable.

## ✨ Características

* **UI/UX Premium:** Interfaz de terminal renderizada con `Rich` y menús interactivos fluidos potenciados por `Questionary`.
* **Motor Asíncrono:** Descargas ultra rápidas y extracción de metadatos sin bloquear la interfaz.
* **Persistencia de Estado:** Recuerda tus preferencias de formato (MP3, FLAC, MP4, MKV), resolución y rutas de descarga localmente.
* **Multiplataforma y Portable:** Distribuido como un binario único. Cero dependencias requeridas para el usuario final.

---

## 🚀 Instalación (Recomendado)

Para usar WOLFCODE en **Linux, Windows o Mac NO es necesario instalar Python ni configurar entornos**.

1. Ve a la sección de [Releases](../../releases) del repositorio.
2. Descarga el ejecutable nativo correspondiente a tu sistema operativo (`wolfcode-linux`, `wolfcode-windows.exe`, etc.).
3. Abre tu terminal y ejecútalo directamente.

---

## 💻 Instalación para Desarrolladores

Si deseas explorar el código fuente, modificar la herramienta o compilarla tú mismo:

```bash
# 1. Clonar el repositorio
git clone [https://github.com/tu-usuario/wolfcode.git](https://github.com/tu-usuario/wolfcode.git)
cd wolfcode

# 2. Crear y activar el entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows usa: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt # o usa Poetry/pipenv si lo configuraste