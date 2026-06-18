"""Fondo geométrico sutil estilo mockup."""

import tkinter as tk

from theme import COLORS


class PatternBackground(tk.Canvas):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, highlightthickness=0, bd=0, bg=COLORS["bg"], **kwargs)
        self.bind("<Configure>", self._draw)

    def _draw(self, _event=None) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        step = 80
        c1, c2 = COLORS["pattern_a"], COLORS["pattern_b"]
        for y in range(-step, h + step, step):
            for x in range(-step, w + step, step):
                if (x // step + y // step) % 2 == 0:
                    self.create_polygon(
                        x, y,
                        x + step, y,
                        x + step, y + step,
                        fill=c1, outline="",
                    )
                else:
                    self.create_polygon(
                        x, y,
                        x, y + step,
                        x + step, y + step,
                        fill=c2, outline="",
                    )
