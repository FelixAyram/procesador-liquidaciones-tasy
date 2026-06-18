"""Contenedor principal con scroll horizontal y vertical."""

import tkinter as tk

from scroll_utils import DarkScrollbar, bind_canvas_mousewheel, sync_scrollbars
from theme import COLORS


class ScrollContainer(tk.Frame):
    """Envuelve el contenido; las barras solo aparecen si hace falta."""

    def __init__(self, master: tk.Misc, *, min_content_width: int | None = None) -> None:
        super().__init__(master, bg=COLORS["pattern_a"])
        self._min_content_width = min_content_width or 0

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, bg=COLORS["pattern_a"], highlightthickness=0, bd=0)
        self._v_scroll = DarkScrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._h_scroll = DarkScrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=self._v_scroll.set, xscrollcommand=self._h_scroll.set)

        self.content = tk.Frame(self._canvas, bg=COLORS["pattern_a"])
        self._window_id = self._canvas.create_window((0, 0), window=self.content, anchor="nw")

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._v_scroll.grid(row=0, column=1, sticky="ns")
        self._h_scroll.grid(row=1, column=0, sticky="ew")
        self._v_scroll.grid_remove()
        self._h_scroll.grid_remove()

        self.content.bind("<Configure>", self._on_content_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        bind_canvas_mousewheel(self._canvas, self._canvas)
        bind_canvas_mousewheel(self._canvas, self.content)

    def _on_content_configure(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        sync_scrollbars(self._canvas, self._v_scroll, self._h_scroll)

    def _on_canvas_configure(self, event) -> None:
        req_w = self.content.winfo_reqwidth()
        req_h = self.content.winfo_reqheight()
        content_w = max(req_w, event.width, self._min_content_width)
        content_h = max(req_h, event.height)
        self._canvas.itemconfigure(self._window_id, width=content_w, height=content_h)
        sync_scrollbars(self._canvas, self._v_scroll, self._h_scroll)
