"""Carga y cache de iconos PNG para la interfaz."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

_BUNDLED_NAMES = {
    "pdf": "pdf.png",
    "excel": "excel.png",
    "process": "process.png",
    "info": "info.png",
}

_DEV_PATHS = {
    "pdf": Path(r"C:\Users\ayram\Downloads\pdf-file-format-symbol.png"),
    "excel": Path(r"C:\Users\ayram\Downloads\clipart4762219.png"),
    "process": Path(r"C:\Users\ayram\Downloads\document-processing.png"),
    "info": Path(r"C:\Users\ayram\Downloads\icons8-info-24.png"),
}


def _assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent / "assets"


def _resolve_icon_path(kind: str) -> Path:
    bundled = _assets_dir() / _BUNDLED_NAMES[kind]
    if bundled.is_file():
        return bundled
    if sys.platform == "win32":
        preferred = _DEV_PATHS.get(kind)
        if preferred and preferred.is_file():
            return preferred
    raise FileNotFoundError(f"No se encontró el icono: {bundled}")


class IconAssets:
    """Mantiene referencias a PhotoImage escaladas (evita garbage collection)."""

    def __init__(self, root: tk.Misc) -> None:
        self._root = root
        self._cache: dict[tuple[str, int], ImageTk.PhotoImage] = {}
        self.paths = {kind: _resolve_icon_path(kind) for kind in _BUNDLED_NAMES}

    def get(self, kind: str, size: int) -> ImageTk.PhotoImage:
        size = max(16, int(size))
        key = (kind, size)
        if key in self._cache:
            return self._cache[key]

        path = self.paths[kind]
        image = Image.open(path)
        if image.mode not in ("RGBA", "RGB"):
            image = image.convert("RGBA")

        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image, master=self._root)
        self._cache[key] = photo
        return photo
