"""Lista de PDFs con iconos, botón borrar siempre visible y scroll vertical."""

import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from drawing import draw_rounded_rect
from icon_assets import IconAssets
from icons import draw_delete_circle
from scroll_utils import DarkScrollbar, bind_canvas_mousewheel, sync_scrollbars, truncate_text
from theme import COLORS, RADIUS, ROW_HEIGHT, AppFonts

_ICON_SLOT = 36
_DELETE_SLOT = 40
_ROW_PAD = 10


class ScrollablePdfList(tk.Frame):
    def __init__(self, master: tk.Misc, fonts: AppFonts, on_remove, *, icon_assets: IconAssets) -> None:
        super().__init__(master, bg=COLORS["surface_card"])
        self.fonts = fonts
        self.on_remove = on_remove
        self._icon_assets = icon_assets
        self._rows: dict[str, tk.Frame] = {}
        self._row_index = 0
        self._name_font = tkfont.Font(font=fonts.list_item)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, bg=COLORS["surface_card"], highlightthickness=0, bd=0)
        self._v_scroll = DarkScrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._v_scroll.set)

        self.inner = tk.Frame(self._canvas, bg=COLORS["surface_card"])
        self._window_id = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._v_scroll.grid(row=0, column=1, sticky="ns")
        self._v_scroll.grid_remove()

        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        bind_canvas_mousewheel(self._canvas, self._canvas)
        bind_canvas_mousewheel(self._canvas, self.inner)

        self._empty_label = tk.Label(
            self.inner,
            text="Sin archivos cargados",
            font=fonts.status,
            fg=COLORS["muted"],
            bg=COLORS["surface_card"],
            anchor="w",
        )

    def _on_inner_configure(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        sync_scrollbars(self._canvas, self._v_scroll, None)

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfigure(self._window_id, width=event.width)
        for row in self._rows.values():
            self._relayout_row(row)
        sync_scrollbars(self._canvas, self._v_scroll, None)

    def _show_empty(self) -> None:
        self._empty_label.pack(fill=tk.X, pady=16, padx=12)

    def _relayout_row(self, row: tk.Frame) -> None:
        meta = getattr(row, "_pdf_meta", None)
        if not meta:
            return

        row_canvas = meta["canvas"]
        w = max(row_canvas.winfo_width(), 80)
        row_h = meta["row_h"]

        row_canvas.delete("bg")
        draw_rounded_rect(row_canvas, 0, 0, w, row_h, RADIUS["sm"], meta["bg"], tags="bg")
        row_canvas.tag_lower("bg")

        row_canvas.coords(meta["pdf_icon_id"], _ICON_SLOT // 2 + 6, row_h // 2)
        row_canvas.coords(meta["del_id"], w - _ROW_PAD, row_h // 2)

        name_max = max(w - _ICON_SLOT - _DELETE_SLOT - _ROW_PAD * 2, 24)
        meta["name_label"].config(text=truncate_text(meta["full_name"], self._name_font, name_max))
        row_canvas.coords(meta["name_id"], _ICON_SLOT + 4, row_h // 2)
        row_canvas.itemconfigure(meta["name_id"], width=name_max)

    def add_pdf(self, pdf_path: Path) -> None:
        key = str(pdf_path)
        if key in self._rows:
            return

        self._empty_label.pack_forget()

        bg = COLORS["surface_row"] if self._row_index % 2 == 0 else COLORS["surface_row_alt"]
        self._row_index += 1

        row_h = ROW_HEIGHT
        row = tk.Frame(self.inner, bg=COLORS["surface_card"], height=row_h + 6)
        row.pack(fill=tk.X, pady=2, padx=2)
        row.pack_propagate(False)

        row_canvas = tk.Canvas(row, height=row_h, bg=COLORS["surface_card"], highlightthickness=0, bd=0)
        row_canvas.pack(fill=tk.BOTH, expand=True)

        pdf_photo = self._icon_assets.get("pdf", 24)
        pdf_icon_id = row_canvas.create_image(_ICON_SLOT // 2 + 6, row_h // 2, image=pdf_photo, anchor="center")
        row_canvas.pdf_photo = pdf_photo

        name_label = tk.Label(
            row_canvas,
            text=pdf_path.name,
            font=self.fonts.list_item,
            fg=COLORS["text"],
            bg=bg,
            anchor="w",
        )
        name_id = row_canvas.create_window(_ICON_SLOT + 4, row_h // 2, window=name_label, anchor="w")

        del_canvas = tk.Canvas(row_canvas, width=30, height=30, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        del_id = row_canvas.create_window(0, row_h // 2, window=del_canvas, anchor="e")
        draw_delete_circle(del_canvas, 15, 15, 13, COLORS["danger_circle"])
        del_canvas.bind("<Button-1>", lambda _e, p=pdf_path: self.on_remove(p))
        del_canvas.bind("<Enter>", lambda _e, c=del_canvas: draw_delete_circle(c, 15, 15, 13, COLORS["danger_hover"]))
        del_canvas.bind("<Leave>", lambda _e, c=del_canvas: draw_delete_circle(c, 15, 15, 13, COLORS["danger_circle"]))

        row._pdf_meta = {
            "canvas": row_canvas,
            "row_h": row_h,
            "bg": bg,
            "full_name": pdf_path.name,
            "name_label": name_label,
            "name_id": name_id,
            "pdf_icon_id": pdf_icon_id,
            "del_id": del_id,
        }
        row_canvas.bind("<Configure>", lambda _e, r=row: self._relayout_row(r))

        self._rows[key] = row
        self._on_inner_configure()

    def remove_pdf(self, pdf_path: Path) -> None:
        row = self._rows.pop(str(pdf_path), None)
        if row:
            row.destroy()
        if not self._rows:
            self._row_index = 0
            self._show_empty()
        self._on_inner_configure()
