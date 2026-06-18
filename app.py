"""Ventana principal de la aplicación."""

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from background import PatternBackground
from excel_export import write_rows_to_excel
from icon_assets import IconAssets
from tooltips import ToolTip
from pdf_list import ScrollablePdfList
from pdf_parser import extract_invoice_data, read_pdf_text
from theme import COLORS, LAYOUT, SPACING, WINDOW, AppFonts, configure_ttk_dark
from widgets import FilePickerCard, ProcessButton, SoftCard


class LiquidacionesApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Procesador de Liquidaciones Tasy")
        self.root.configure(bg=COLORS["bg"])

        self.pdf_files: list[Path] = []
        self.excel_file: Path | None = None
        self.fonts = AppFonts(root)
        self.icon_assets = IconAssets(root)

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self) -> None:
        configure_ttk_dark(ttk.Style(), self.fonts.family)

    def _build_ui(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Marco principal con tamaño fijo — evita que Tk encoja la ventana.
        shell = tk.Frame(
            self.root,
            bg=COLORS["bg"],
            width=WINDOW["width"],
            height=WINDOW["height"],
        )
        shell.grid(row=0, column=0, sticky="nsew")
        shell.grid_propagate(False)
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=1)

        bg = PatternBackground(shell)
        bg.place(x=0, y=0, relwidth=1, relheight=1)

        pad = SPACING["lg"]
        container = tk.Frame(shell, bg=COLORS["bg"], padx=pad, pady=pad)
        container.place(x=0, y=0, relwidth=1, relheight=1)
        container.grid_columnconfigure(0, weight=0, minsize=LAYOUT["left_panel"])
        container.grid_columnconfigure(1, weight=1, minsize=LAYOUT["right_panel"])
        container.grid_rowconfigure(0, weight=1)

        self._build_left_panel(container)
        self._build_right_panel(container)

    def _build_left_panel(self, parent: tk.Frame) -> None:
        left = tk.Frame(parent, bg=COLORS["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["md"]))
        left.grid_rowconfigure(0, weight=1, minsize=LAYOUT["card_min_height"])
        left.grid_rowconfigure(1, weight=1, minsize=LAYOUT["card_min_height"])
        left.grid_columnconfigure(0, weight=1, minsize=LAYOUT["left_panel"])

        self.pdf_card = FilePickerCard(
            left,
            title="Seleccionar PDF",
            icon="pdf",
            command=self.add_pdfs,
            dashed=True,
            font=self.fonts.action,
            icon_assets=self.icon_assets,
        )
        self.pdf_card.grid(row=0, column=0, sticky="nsew", pady=(0, SPACING["md"]))

        self.excel_card = FilePickerCard(
            left,
            title="Seleccionar Excel (.xlsx)",
            icon="excel",
            command=self.add_excel,
            dashed=False,
            font=self.fonts.action,
            icon_assets=self.icon_assets,
        )
        self.excel_card.grid(row=1, column=0, sticky="nsew")

        self.excel_status = tk.Label(
            left,
            text="",
            font=self.fonts.status,
            fg=COLORS["muted"],
            bg=COLORS["bg"],
            wraplength=290,
            justify=tk.LEFT,
            anchor="w",
        )
        self.excel_status.grid(row=2, column=0, sticky="ew", pady=(SPACING["sm"], 0))

    def _build_right_panel(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=COLORS["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1, minsize=LAYOUT["list_min_height"] + 48)
        right.grid_rowconfigure(1, weight=0, minsize=LAYOUT["process_btn_height"])
        right.grid_columnconfigure(0, weight=1, minsize=LAYOUT["right_panel"])

        list_panel = SoftCard(right, padding=SPACING["md"], expand=True)
        list_panel.grid(row=0, column=0, sticky="nsew", pady=(0, SPACING["md"]))
        list_panel.content.grid_rowconfigure(1, weight=1, minsize=LAYOUT["list_min_height"])
        list_panel.content.grid_columnconfigure(0, weight=1)

        tk.Label(
            list_panel.content,
            text="PDF seleccionados",
            font=self.fonts.section,
            fg=COLORS["text"],
            bg=COLORS["surface_card"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, SPACING["sm"]))

        self.pdf_list = ScrollablePdfList(
            list_panel.content,
            self.fonts,
            self.remove_pdf,
            icon_assets=self.icon_assets,
        )
        self.pdf_list.grid(row=1, column=0, sticky="nsew")

        ProcessButton(
            right,
            command=self.process_documents,
            font=self.fonts.process,
            icon_assets=self.icon_assets,
        ).grid(
            row=1, column=0, sticky="ew", ipady=4
        )

        footer = tk.Frame(right, bg=COLORS["bg"])
        footer.grid(row=2, column=0, sticky="ew", pady=(SPACING["md"], 0))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            footer,
            text="Listo para procesar",
            font=self.fonts.status,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg"],
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        info_photo = self.icon_assets.get("info", 22)
        info_btn = tk.Label(footer, image=info_photo, bg=COLORS["bg"], cursor="hand2")
        info_btn.image = info_photo
        info_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))
        ToolTip(info_btn, "created by @felixayram33@gmail.com")

    def _refresh_pdf_count_status(self) -> None:
        count = len(self.pdf_files)
        if count == 0:
            self.status_label.config(text="Listo para procesar")
        elif count == 1:
            self.status_label.config(text="Listo: 1 PDF cargado")
        else:
            self.status_label.config(text=f"Listo: {count} PDFs cargados")

    def _format_excel_path(self, path: Path) -> str:
        text = str(path)
        if len(text) > 52:
            return f"Ubicación Base de Datos: [...]/{path.name}"
        return f"Ubicación Base de Datos: {text}"

    def add_pdfs(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        for path in paths:
            pdf_path = Path(path)
            if pdf_path not in self.pdf_files:
                self.pdf_files.append(pdf_path)
                self.pdf_list.add_pdf(pdf_path)
        self._refresh_pdf_count_status()

    def remove_pdf(self, pdf_path: Path) -> None:
        if pdf_path in self.pdf_files:
            self.pdf_files.remove(pdf_path)
        self.pdf_list.remove_pdf(pdf_path)
        self._refresh_pdf_count_status()

    def add_excel(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar plantilla Excel",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
        )
        if path:
            self.excel_file = Path(path)
            formatted = self._format_excel_path(self.excel_file)
            self.excel_card.set_path_text(formatted)
            self.excel_status.config(text=formatted)

    def process_documents(self) -> None:
        if not self.pdf_files:
            messagebox.showwarning("Faltan archivos", "Agregá al menos un archivo PDF.")
            return
        if not self.excel_file:
            messagebox.showwarning("Falta plantilla", "Agregá el archivo Excel (.xlsx) de plantilla.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Guardar resultado",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"Liquidaciones_procesadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        )
        if not output_path:
            return

        try:
            extracted_rows = []
            errors = []

            for pdf_path in self.pdf_files:
                try:
                    text = read_pdf_text(pdf_path)
                    if not text.strip():
                        errors.append(f"{pdf_path.name}: no se pudo leer texto del PDF.")
                        continue
                    extracted_rows.append(extract_invoice_data(text))
                except Exception as exc:
                    errors.append(f"{pdf_path.name}: {exc}")

            if not extracted_rows:
                messagebox.showerror(
                    "Sin datos",
                    "No se pudieron extraer datos de ningún PDF.\n\n" + "\n".join(errors),
                )
                return

            write_rows_to_excel(self.excel_file, Path(output_path), extracted_rows)

            summary = f"Procesados: {len(extracted_rows)} PDF(s). Guardado en:\n{output_path}"
            if errors:
                summary += "\n\nAdvertencias:\n" + "\n".join(errors)

            self.status_label.config(
                text=f"Listo: exportación completada · {len(extracted_rows)} registro(s)"
            )
            messagebox.showinfo("Proceso completado", summary)

        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo procesar:\n{exc}")
