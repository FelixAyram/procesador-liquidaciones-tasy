"""Tamaño de ventana FORZADO vía Win32 — sin cálculos adaptativos."""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk

# Tamaño fijo en píxeles (no se adapta a resolución virtual ni escala).
FORCED_WIDTH = 1000
FORCED_HEIGHT = 720

SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040


def enable_windows_dpi() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def _hwnd(root: tk.Tk) -> int:
    return int(root.winfo_id())


def _set_pos_size(root: tk.Tk, x: int, y: int, w: int, h: int) -> None:
    if sys.platform != "win32":
        root.geometry(f"{w}x{h}+{x}+{y}")
        return
    ctypes.windll.user32.SetWindowPos(
        _hwnd(root), 0, x, y, w, h, SWP_NOZORDER | SWP_SHOWWINDOW
    )


def force_window(root: tk.Tk) -> None:
    """Fuerza 1000x720 centrado con API de Windows."""
    w, h = FORCED_WIDTH, FORCED_HEIGHT

    root.resizable(True, True)
    root.minsize(w, h)
    root.geometry(f"{w}x{h}")

    if sys.platform == "win32":
        sw = int(ctypes.windll.user32.GetSystemMetrics(0))
        sh = int(ctypes.windll.user32.GetSystemMetrics(1))
    else:
        sw, sh = 1920, 1080

    x = max(0, (sw - w) // 2)
    y = max(0, (sh - h) // 2)

    def _apply() -> None:
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.minsize(w, h)
        _set_pos_size(root, x, y, w, h)
        # Si Tk reporta menos, volver a forzar.
        try:
            root.update_idletasks()
            if root.winfo_width() < w - 2 or root.winfo_height() < h - 2:
                _set_pos_size(root, x, y, w, h)
        except tk.TclError:
            pass

    root.bind("<Map>", lambda _e: _apply(), add="+")
    root.after_idle(_apply)
    for delay in (1, 50, 150, 400, 800):
        root.after(delay, _apply)


def init_root_window(root: tk.Tk) -> None:
    root.minsize(FORCED_WIDTH, FORCED_HEIGHT)
    root.geometry(f"{FORCED_WIDTH}x{FORCED_HEIGHT}")
    root.resizable(True, True)


def finalize_root_window(root: tk.Tk) -> None:
    force_window(root)
