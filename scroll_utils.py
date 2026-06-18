"""Scrollbars oscuros, tooltips y rueda del ratón (Windows + Linux)."""

import sys
import tkinter as tk
import tkinter.font as tkfont

from theme import COLORS


class DarkScrollbar(tk.Scrollbar):
    """Scrollbar nativo con colores del tema oscuro (mejor que ttk en Windows)."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(
            master,
            bg=COLORS["surface_hover"],
            troughcolor=COLORS["surface_muted"],
            activebackground=COLORS["border"],
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
            **kwargs,
        )


def truncate_text(text: str, font: tkfont.Font, max_px: int) -> str:
    if max_px < 24 or font.measure(text) <= max_px:
        return text
    ellipsis = "..."
    for end in range(len(text), 0, -1):
        candidate = text[:end] + ellipsis
        if font.measure(candidate) <= max_px:
            return candidate
    return ellipsis


def sync_scrollbars(
    canvas: tk.Canvas,
    v_scroll: tk.Scrollbar | None,
    h_scroll: tk.Scrollbar | None,
) -> None:
    """Muestra u oculta barras solo cuando el contenido no entra en el canvas."""
    canvas.update_idletasks()
    bbox = canvas.bbox("all")
    if not bbox:
        if v_scroll:
            v_scroll.grid_remove()
        if h_scroll:
            h_scroll.grid_remove()
        return

    cw = max(canvas.winfo_width(), 1)
    ch = max(canvas.winfo_height(), 1)
    content_w = bbox[2] - bbox[0]
    content_h = bbox[3] - bbox[1]

    need_v = content_h > ch + 1
    need_h = content_w > cw + 1

    if v_scroll:
        if need_v:
            v_scroll.grid()
        else:
            v_scroll.grid_remove()
            canvas.yview_moveto(0)

    if h_scroll:
        if need_h:
            h_scroll.grid()
        else:
            h_scroll.grid_remove()
            canvas.xview_moveto(0)


def bind_canvas_mousewheel(canvas: tk.Canvas, widget: tk.Misc) -> None:
    """Rueda del ratón: MouseWheel (Windows/macOS) y Button-4/5 (Linux)."""

    def _scroll(delta: int) -> None:
        if delta:
            canvas.yview_scroll(int(-delta), "units")

    def _on_wheel(event) -> None:
        if event.delta:
            _scroll(int(-event.delta / 120))

    def _on_linux_up(_event) -> None:
        _scroll(1)

    def _on_linux_down(_event) -> None:
        _scroll(-1)

    def _on_enter(_event=None) -> None:
        if sys.platform.startswith("linux"):
            canvas.bind_all("<Button-4>", _on_linux_up)
            canvas.bind_all("<Button-5>", _on_linux_down)
        else:
            canvas.bind_all("<MouseWheel>", _on_wheel)

    def _on_leave(_event=None) -> None:
        try:
            if sys.platform.startswith("linux"):
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            else:
                canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass

    widget.bind("<Enter>", _on_enter)
    widget.bind("<Leave>", _on_leave)
