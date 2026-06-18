"""Iconos vectoriales auxiliares (eliminar, play, sparkle)."""

import tkinter as tk


def draw_delete_circle(canvas: tk.Canvas, cx: int, cy: int, radius: int, bg: str = "#e85d5d") -> None:
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=bg, outline="")
    canvas.create_text(cx, cy, text="✕", fill="white", font=("Segoe UI", max(9, radius), "bold"))


def draw_play_dots(canvas: tk.Canvas, cx: int, cy: int, size: int, color: str = "white") -> None:
    r = max(2, size // 10)
    offsets = [(0, -size * 0.22), (-size * 0.18, size * 0.12), (size * 0.18, size * 0.12)]
    for ox, oy in offsets:
        canvas.create_oval(cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r, fill=color, outline="")
