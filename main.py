"""Punto de entrada de la aplicación."""

import sys
import tkinter as tk
from pathlib import Path

from app import LiquidacionesApp
from window_setup import enable_windows_dpi, finalize_root_window, init_root_window


def _assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent / "assets"


def _set_window_icon(root: tk.Tk) -> None:
    assets = _assets_dir()
    ico = assets / "app.ico"
    png = assets / "copybook.png"

    if sys.platform == "win32" and ico.is_file():
        root.iconbitmap(default=str(ico))
        return

    if png.is_file():
        try:
            from PIL import Image, ImageTk

            image = Image.open(png).convert("RGBA")
            image.thumbnail((64, 64))
            photo = ImageTk.PhotoImage(image, master=root)
            root.iconphoto(True, photo)
            root._app_icon = photo  # evitar garbage collection
        except Exception:
            pass


def main() -> None:
    enable_windows_dpi()
    root = tk.Tk()
    init_root_window(root)
    _set_window_icon(root)
    LiquidacionesApp(root)
    finalize_root_window(root)
    root.mainloop()


if __name__ == "__main__":
    main()
