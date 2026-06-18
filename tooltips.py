"""Tooltips simples para widgets Tk."""

import tkinter as tk

from theme import COLORS


class ToolTip:
    def __init__(self, widget: tk.Misc, text: str) -> None:
        self._widget = widget
        self._text = text
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None) -> None:
        if self._tip:
            return
        x = self._widget.winfo_rootx() + 10
        y = self._widget.winfo_rooty() - 32
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tip,
            text=self._text,
            font=("Segoe UI", 10),
            bg=COLORS["surface_card"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            padx=10,
            pady=6,
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        ).pack()

    def _hide(self, _event=None) -> None:
        if self._tip:
            self._tip.destroy()
            self._tip = None
