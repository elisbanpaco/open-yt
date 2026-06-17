try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        config_file="config.toml",
        config_file_parser=tomllib,
        extra="ignore",
    )

    download_path: Path = Field(
        default=Path.home() / "Downloads",
        description="Directorio de descargas predeterminado",
    )
    default_audio_format: str = Field(
        default="mp3",
        description="Formato de audio predeterminado",
    )
    default_video_res: str = Field(
        default="1080",
        description="Resolución de video predeterminada",
    )
    default_audio_quality: str = Field(
        default="320",
        description="Calidad de audio predeterminada en kbps",
    )
    default_video_format: str = Field(
        default="mp4",
        description="Formato de video predeterminado",
    )
    embed_thumbnail: bool = Field(
        default=True,
        description="Incrustar portada en archivos de audio",
    )

    @classmethod
    def get_config_path(cls) -> Path:
        """Obtiene la ruta del archivo de configuración."""
        config_dir = Path.home() / ".config" / "music-free"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.toml"

    @classmethod
    def load(cls) -> "Settings":
        """Carga la configuración desde el archivo TOML."""
        config_path = cls.get_config_path()
        if config_path.exists():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            return cls(**data)
        return cls()

    def save(self) -> None:
        """Guarda la configuración en el archivo TOML."""
        config_path = self.get_config_path()
        config_dict = {
            "download_path": str(self.download_path),
            "default_audio_format": self.default_audio_format,
            "default_video_res": self.default_video_res,
            "default_audio_quality": self.default_audio_quality,
            "default_video_format": self.default_video_format,
            "embed_thumbnail": self.embed_thumbnail,
        }
        
        try:
            import tomli_w
            with open(config_path, "wb") as f:
                tomli_w.dump(config_dict, f)
        except ImportError:
            toml_content = f"""# Configuración de music-free

download_path = "{self.download_path}"
default_audio_format = "{self.default_audio_format}"
default_video_res = "{self.default_video_res}"
default_audio_quality = "{self.default_audio_quality}"
default_video_format = "{self.default_video_format}"
"""
            with open(config_path, "w") as f:
                f.write(toml_content)

    @classmethod
    def get_default_download_path(cls) -> Path:
        """Obtiene la carpeta de Descargas del sistema operativo."""
        if (Path.home() / "Downloads").exists():
            return Path.home() / "Downloads"
        if (Path.home() / "downloads").exists():
            return Path.home() / "downloads"
        return Path.home()


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Obtiene la instancia global de configuración."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings.load()
    return _settings_instance


def reload_settings() -> Settings:
    """Recarga la configuración desde el archivo."""
    global _settings_instance
    _settings_instance = Settings.load()
    return _settings_instance
