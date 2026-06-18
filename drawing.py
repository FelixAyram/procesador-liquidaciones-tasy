"""Utilidades de dibujo: rectángulos redondeados y fondos."""

import tkinter as tk

from theme import COLORS


def widget_bg(widget: tk.Misc) -> str:
    try:
        return widget.cget("bg")
    except tk.TclError:
        return COLORS["bg"]


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    radius: int,
    fill: str,
    outline: str = "",
    *,
    tags: str | tuple[str, ...] = "",
) -> list[int]:
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    kw = {"fill": fill, "outline": outline, "tags": tags}
    return [
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, **kw),
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, **kw),
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, **kw),
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, **kw),
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kw),
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kw),
    ]
