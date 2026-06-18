"""Design tokens — estilo mockup oscuro con acentos verdes."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

COLORS = {
    "bg": "#0d1118",
    "pattern_a": "#10151f",
    "pattern_b": "#0d1118",
    "surface": "#1a2030",
    "surface_card": "#222836",
    "surface_hover": "#2a3142",
    "surface_muted": "#181e2b",
    "surface_row": "#252b3a",
    "surface_row_alt": "#1e2433",
    "primary": "#e2e8f0",
    "primary_hover": "#ffffff",
    "primary_soft": "#334155",
    "success": "#22a55b",
    "success_hover": "#1d8f4e",
    "success_light": "#3dd68c",
    "success_dark": "#178a47",
    "success_soft": "#14532d",
    "danger": "#f87171",
    "danger_hover": "#ef4444",
    "danger_bg": "#e85d5d",
    "danger_circle": "#e85d5d",
    "text": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "muted": "#8b95a8",
    "border": "#3a4256",
    "border_dashed": "#4a5568",
    "shadow": "#05070c",
    "shadow_deep": "#000000",
    "header_excel": "#1E1B4B",
    "card": "#222836",
    "accent": "#22a55b",
    "accent_hover": "#1d8f4e",
}

RADIUS = {"sm": 10, "md": 14, "lg": 18}
SHADOW_OFFSET = 5
SPACING = {"sm": 8, "md": 16, "lg": 24}
ROW_HEIGHT = 40

# Tamaño fijo de ventana (ver window_setup.py).
WINDOW = {
    "width": 1000,
    "height": 720,
}
LAYOUT = {
    "left_panel": 300,
    "right_panel": 560,
    "card_min_height": 190,
    "list_min_height": 220,
    "process_btn_height": 56,
}


def resolve_font_family(root: tk.Misc) -> str:
    available = {name.lower(): name for name in tkfont.families(root)}
    for candidate in ("Segoe UI", "Calibri", "Tahoma", "Arial"):
        if candidate.lower() in available:
            return available[candidate.lower()]
    return tkfont.nametofont("TkDefaultFont").cget("family")


class AppFonts:
    def __init__(self, root: tk.Misc) -> None:
        family = resolve_font_family(root)
        self.family = family
        self.section = (family, 18, "bold")
        self.action = (family, 14, "bold")
        self.list_item = (family, 12)
        self.status = (family, 11)
        self.remove_btn = (family, 10, "bold")
        self.process = (family, 18, "bold")


def enable_windows_dpi_awareness() -> None:
    """Compatibilidad — usar window_setup.enable_windows_dpi()."""
    from window_setup import enable_windows_dpi

    enable_windows_dpi()


def apply_ui_scaling(_root: tk.Tk) -> None:
    """Sin escalado extra: evita ventanas minúsculas en .exe con PyInstaller."""
    pass


def configure_ttk_dark(style: ttk.Style, family: str) -> None:
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure(".", font=(family, 12), background=COLORS["bg"], foreground=COLORS["text"])
    style.configure(
        "TScrollbar",
        background=COLORS["surface_hover"],
        troughcolor=COLORS["surface_muted"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["text_secondary"],
        gripcount=0,
    )
    style.map(
        "TScrollbar",
        background=[("active", COLORS["border"]), ("pressed", COLORS["border"])],
        troughcolor=[("active", COLORS["surface_muted"])],
    )
