"""Lectura y extracción de datos de facturas PDF (AFIP)."""

import re
from datetime import datetime
from pathlib import Path

import pdfplumber


def parse_amount(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("$", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_first_invoice_text(full_text: str) -> str:
    markers = ["DUPLICADO", "TRIPLICADO", "CUADRIPLICADO"]
    end = len(full_text)
    for marker in markers:
        idx = full_text.find(marker)
        if idx > 0:
            end = min(end, idx)
    return full_text[:end]


def read_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def extract_invoice_data(text: str) -> dict:
    text = extract_first_invoice_text(text)
    data: dict = {}

    match = re.search(
        r"Raz[oó]n Social:\s*(.+?)(?:\s+Fecha de Emisi[oó]n:)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    data["a y n"] = match.group(1).strip() if match else ""

    match = re.search(
        r"Domicilio Comercial:.*?CUIT:\s*(\d{11})",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    data["cuit"] = match.group(1) if match else ""

    match = re.search(r"Importe Exento:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
    data["exento"] = parse_amount(match.group(1)) if match else 0.0

    match = re.search(r"IVA 10[,.]?5%:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
    data["iva10,5 "] = parse_amount(match.group(1)) if match else 0.0

    match = re.search(r"IVA 21%:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
    data["iva 21"] = parse_amount(match.group(1)) if match else 0.0

    gr_10_5 = 0.0
    gr_21 = 0.0
    for line in text.splitlines():
        if re.search(r"10[,.]5\s*%", line, re.IGNORECASE):
            numbers = re.findall(r"([\d.,]+)", line)
            if len(numbers) >= 3:
                gr_10_5 += parse_amount(numbers[-3])
        elif re.search(r"\b21\s*%", line) and "IVA 21" not in line:
            numbers = re.findall(r"([\d.,]+)", line)
            if len(numbers) >= 3:
                gr_21 += parse_amount(numbers[-3])

    if gr_10_5 == 0.0 and data["iva10,5 "] > 0:
        match = re.search(r"Importe Neto Gravado:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
        if match:
            gr_10_5 = parse_amount(match.group(1))

    if gr_21 == 0.0 and data["iva 21"] > 0:
        match = re.search(r"Importe Neto Gravado:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
        if match:
            gr_21 = parse_amount(match.group(1))

    data["gr10,5"] = gr_10_5
    data["gr 21"] = gr_21

    match = re.search(r"Importe Total:\s*\$?\s*([\d.,]+)", text, re.IGNORECASE)
    data["total"] = parse_amount(match.group(1)) if match else 0.0

    match = re.search(r"Fecha de Emisi[oó]n:\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    data["fecha"] = match.group(1) if match else ""

    match = re.search(
        r"Fecha de Vto\. para el pago:\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )
    data["fecha pago"] = match.group(1) if match else ""

    match = re.search(r"Punto de Venta:\s*(\d+)", text, re.IGNORECASE)
    data["punto"] = match.group(1) if match else ""

    match = re.search(r"Comp\. Nro:\s*(\d+)", text, re.IGNORECASE)
    data["nro"] = match.group(1) if match else ""

    match = re.search(r"COD\.\s*(\d+)", text, re.IGNORECASE)
    data["cpte"] = match.group(1) if match else ""

    match = re.search(r"CAE N[°º]:\s*(\d+)", text, re.IGNORECASE)
    data["cae"] = match.group(1) if match else ""

    match = re.search(
        r"Fecha de Vto\. de CAE:\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )
    data["fecha cae"] = match.group(1) if match else ""

    match = re.search(
        r"Per[ií]odo Facturado Desde:\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )
    if match:
        period_date = datetime.strptime(match.group(1), "%d/%m/%Y")
        data["anio_periodo"] = period_date.year
        data["mes_periodo"] = period_date.month
    else:
        data["anio_periodo"] = ""
        data["mes_periodo"] = ""

    match = re.search(
        r"CUIT:\s*\d+\s+Apellido y Nombre / Raz[oó]n Social:\s*([^\n]+)",
        text,
        re.IGNORECASE,
    )
    data["sigla_clinica"] = match.group(1).strip() if match else ""

    if re.search(r"\nA\s*\n\s*FACTURA", text, re.IGNORECASE):
        data["letra"] = "A"
    elif re.search(r"\nB\s*\n\s*FACTURA", text, re.IGNORECASE):
        data["letra"] = "B"
    elif re.search(r"\nC\s*\n\s*FACTURA", text, re.IGNORECASE):
        data["letra"] = "C"
    else:
        data["letra"] = ""

    data["strad"] = ""
    data[0] = 0.0
    data["alquiler"] = 0
    data["perce"] = 0
    data["fecha proceso"] = datetime.now().strftime("%d/%m/%Y")

    return data
