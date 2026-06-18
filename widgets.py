"""Componentes UI: tarjetas de selección, botón procesar, tarjetas."""

import tkinter as tk

from drawing import draw_rounded_rect, widget_bg
from icon_assets import IconAssets
from theme import COLORS, RADIUS, SHADOW_OFFSET


class FilePickerCard(tk.Frame):
    """Tarjeta clickeable con icono grande (PDF o Excel)."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        title: str,
        icon: str,
        command,
        dashed: bool = False,
        font,
        icon_assets: IconAssets,
    ) -> None:
        bg = widget_bg(master)
        super().__init__(master, bg=bg)
        self._command = command
        self._title = title
        self._icon = icon
        self._dashed = dashed
        self._font = font
        self._icon_assets = icon_assets
        self._hover = False
        self._path_text = ""
        self._icon_photo = None

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg, cursor="hand2", height=160)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._redraw())
        self.canvas.bind("<Enter>", lambda _e: self._set_hover(True))
        self.canvas.bind("<Leave>", lambda _e: self._set_hover(False))
        self.canvas.bind("<Button-1>", lambda _e: self._command())

    def set_path_text(self, text: str) -> None:
        self._path_text = text
        self._redraw()

    def _set_hover(self, state: bool) -> None:
        self._hover = state
        self._redraw()

    def _redraw(self) -> None:
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 120)
        h = max(self.canvas.winfo_height(), 160)
        fill = COLORS["surface_hover"] if self._hover else COLORS["surface_card"]
        r = RADIUS["lg"]

        draw_rounded_rect(self.canvas, 4, 4, w, h, r, COLORS["shadow"])
        draw_rounded_rect(self.canvas, 0, 0, w - 4, h - 4, r, fill)

        outline = COLORS["border_dashed"] if self._dashed else COLORS["border"]
        dash = (6, 4) if self._dashed else ()
        self.canvas.create_rectangle(
            8, 8, w - 12, h - 12,
            outline=outline, width=2, dash=dash,
        )

        icon_y = h * 0.38
        icon_size = int(min(w, h) * 0.42)
        self._icon_photo = self._icon_assets.get(self._icon, icon_size)
        self.canvas.create_image(w / 2 - 2, icon_y, image=self._icon_photo, anchor="center")

        self.canvas.create_text(
            w / 2 - 2, h * 0.72,
            text=self._title,
            fill=COLORS["text"],
            font=self._font,
            width=w - 24,
            justify=tk.CENTER,
        )

        if self._path_text:
            box_y1 = h * 0.82
            self.canvas.create_rectangle(14, box_y1, w - 18, h - 14, fill=COLORS["surface_muted"], outline=COLORS["border"])
            self.canvas.create_text(
                w / 2 - 2, (box_y1 + h - 14) / 2,
                text=self._path_text,
                fill=COLORS["muted"],
                font=("Segoe UI", 9),
                width=w - 36,
                justify=tk.CENTER,
            )


class ProcessButton(tk.Frame):
    """Botón verde con icono de procesamiento."""

    def __init__(self, master: tk.Misc, *, command, font, icon_assets: IconAssets) -> None:
        bg = widget_bg(master)
        super().__init__(master, bg=bg)
        self._command = command
        self._font = font
        self._icon_assets = icon_assets
        self._hover = False
        self._pressed = False
        self._icon_photo = None

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg, cursor="hand2", height=56)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._redraw())
        self.canvas.bind("<Enter>", lambda _e: self._set_hover(True))
        self.canvas.bind("<Leave>", lambda _e: self._set_hover(False))
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def _set_hover(self, state: bool) -> None:
        self._hover = state
        if not self._pressed:
            self._redraw()

    def _on_press(self, _event) -> None:
        self._pressed = True
        self._redraw()

    def _on_release(self, event) -> None:
        inside = 0 <= event.x <= self.canvas.winfo_width() and 0 <= event.y <= self.canvas.winfo_height()
        self._pressed = False
        self._redraw()
        if inside:
            self._command()

    def _button_color(self) -> str:
        if self._pressed:
            return COLORS["success_dark"]
        if self._hover:
            return COLORS["success_hover"]
        return COLORS["success"]

    def _redraw(self) -> None:
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 200)
        h = max(self.canvas.winfo_height(), 52)
        r = RADIUS["lg"]
        bw, bh = w - 2, h - 2
        fill = self._button_color()

        draw_rounded_rect(self.canvas, 2, 2, w, h, r, COLORS["shadow"])
        draw_rounded_rect(self.canvas, 0, 0, bw, bh, r, fill)
        self.canvas.create_text(bw * 0.42, bh / 2, text="Procesar datos", fill="white", font=self._font, anchor="e")

        icon_size = min(36, int(bh * 0.62))
        self._icon_photo = self._icon_assets.get("process", icon_size)
        self.canvas.create_image(bw * 0.78, bh / 2, image=self._icon_photo, anchor="center")


class SoftCard(tk.Frame):
    def __init__(self, master: tk.Misc, *, padding: int = 20, expand: bool = False) -> None:
        bg = widget_bg(master)
        super().__init__(master, bg=bg)
        self._padding = padding

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg)
        self.canvas.pack(fill=tk.BOTH, expand=expand)
        self.content = tk.Frame(self.canvas, bg=COLORS["surface_card"])
        self._window = self.canvas.create_window((padding, padding), window=self.content, anchor="nw")
        self.canvas.bind("<Configure>", self._on_configure)

    def _on_configure(self, _event=None) -> None:
        w = max(self.canvas.winfo_width(), 60)
        h = max(self.canvas.winfo_height(), 60)
        self.canvas.delete("card")
        draw_rounded_rect(self.canvas, SHADOW_OFFSET, SHADOW_OFFSET, w, h, RADIUS["lg"], COLORS["shadow"])
        draw_rounded_rect(self.canvas, 0, 0, w - SHADOW_OFFSET, h - SHADOW_OFFSET, RADIUS["lg"], COLORS["surface_card"])
        inner_w = max(w - SHADOW_OFFSET - 2 * self._padding, 40)
        inner_h = max(h - SHADOW_OFFSET - 2 * self._padding, 40)
        self.canvas.coords(self._window, self._padding, self._padding)
        self.canvas.itemconfigure(self._window, width=inner_w, height=inner_h)
