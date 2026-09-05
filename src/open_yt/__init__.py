import importlib.metadata

try:
    __version__ = importlib.metadata.version("open-yt")
except Exception:
    __version__ = "0.1.3.1"
