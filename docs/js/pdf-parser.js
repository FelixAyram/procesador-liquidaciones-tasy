/** Lectura y extracción de datos de facturas PDF (AFIP) — versión navegador. */

export function parseAmount(value) {
  if (!value) return 0.0;
  let cleaned = value.replace(/\$/g, "").trim();
  cleaned = cleaned.replace(/\./g, "").replace(",", ".");
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? n : 0.0;
}

export function extractFirstInvoiceText(fullText) {
  const markers = ["DUPLICADO", "TRIPLICADO", "CUADRIPLICADO"];
  let end = fullText.length;
  for (const marker of markers) {
    const idx = fullText.indexOf(marker);
    if (idx > 0) end = Math.min(end, idx);
  }
  return fullText.slice(0, end);
}

/** Agrupa items de pdf.js en líneas (similar a pdfplumber). */
export function groupTextItemsIntoLines(items) {
  const lineMap = new Map();
  for (const item of items) {
    const str = item.str;
    if (!str || !str.trim()) continue;
    const y = Math.round(item.transform[5]);
    if (!lineMap.has(y)) lineMap.set(y, []);
    lineMap.get(y).push({ x: item.transform[4], str });
  }
  return [...lineMap.keys()]
    .sort((a, b) => b - a)
    .map((y) =>
      lineMap
        .get(y)
        .sort((a, b) => a.x - b.x)
        .map((p) => p.str)
        .join(" ")
    );
}

export async function readPdfText(arrayBuffer, pdfjsLib) {
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer.slice(0) }).promise;
  const parts = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    parts.push(groupTextItemsIntoLines(content.items).join("\n"));
  }
  return parts.join("\n");
}

export function extractInvoiceData(text) {
  text = extractFirstInvoiceText(text);
  const data = {};

  let match = text.match(
    /Raz[oó]n Social:\s*(.+?)(?:\s+Fecha de Emisi[oó]n:)/is
  );
  data["a y n"] = match ? match[1].trim() : "";

  match = text.match(/Domicilio Comercial:.*?CUIT:\s*(\d{11})/is);
  data.cuit = match ? match[1] : "";

  match = text.match(/Importe Exento:\s*\$?\s*([\d.,]+)/i);
  data.exento = match ? parseAmount(match[1]) : 0.0;

  match = text.match(/IVA 10[,.]?5%:\s*\$?\s*([\d.,]+)/i);
  data["iva10,5 "] = match ? parseAmount(match[1]) : 0.0;

  match = text.match(/IVA 21%:\s*\$?\s*([\d.,]+)/i);
  data["iva 21"] = match ? parseAmount(match[1]) : 0.0;

  let gr10_5 = 0.0;
  let gr21 = 0.0;
  for (const line of text.split(/\r?\n/)) {
    if (/10[,.]5\s*%/i.test(line)) {
      const numbers = line.match(/([\d.,]+)/g);
      if (numbers && numbers.length >= 3) gr10_5 += parseAmount(numbers[numbers.length - 3]);
    } else if (/\b21\s*%/.test(line) && !/IVA 21/i.test(line)) {
      const numbers = line.match(/([\d.,]+)/g);
      if (numbers && numbers.length >= 3) gr21 += parseAmount(numbers[numbers.length - 3]);
    }
  }

  if (gr10_5 === 0.0 && data["iva10,5 "] > 0) {
    match = text.match(/Importe Neto Gravado:\s*\$?\s*([\d.,]+)/i);
    if (match) gr10_5 = parseAmount(match[1]);
  }

  if (gr21 === 0.0 && data["iva 21"] > 0) {
    match = text.match(/Importe Neto Gravado:\s*\$?\s*([\d.,]+)/i);
    if (match) gr21 = parseAmount(match[1]);
  }

  data["gr10,5"] = gr10_5;
  data["gr 21"] = gr21;

  match = text.match(/Importe Total:\s*\$?\s*([\d.,]+)/i);
  data.total = match ? parseAmount(match[1]) : 0.0;

  match = text.match(/Fecha de Emisi[oó]n:\s*(\d{2}\/\d{2}\/\d{4})/i);
  data.fecha = match ? match[1] : "";

  match = text.match(/Fecha de Vto\. para el pago:\s*(\d{2}\/\d{2}\/\d{4})/i);
  data["fecha pago"] = match ? match[1] : "";

  match = text.match(/Punto de Venta:\s*(\d+)/i);
  data.punto = match ? match[1] : "";

  match = text.match(/Comp\. Nro:\s*(\d+)/i);
  data.nro = match ? match[1] : "";

  match = text.match(/COD\.\s*(\d+)/i);
  data.cpte = match ? match[1] : "";

  match = text.match(/CAE N[°º]:\s*(\d+)/i);
  data.cae = match ? match[1] : "";

  match = text.match(/Fecha de Vto\. de CAE:\s*(\d{2}\/\d{2}\/\d{4})/i);
  data["fecha cae"] = match ? match[1] : "";

  match = text.match(/Per[ií]odo Facturado Desde:\s*(\d{2}\/\d{2}\/\d{4})/i);
  if (match) {
    const [d, m, y] = match[1].split("/").map(Number);
    data.anio_periodo = y;
    data.mes_periodo = m;
  } else {
    data.anio_periodo = "";
    data.mes_periodo = "";
  }

  match = text.match(
    /CUIT:\s*\d+\s+Apellido y Nombre \/ Raz[oó]n Social:\s*([^\n]+)/i
  );
  data.sigla_clinica = match ? match[1].trim() : "";

  if (/\nA\s*\n\s*FACTURA/is.test(text)) data.letra = "A";
  else if (/\nB\s*\n\s*FACTURA/is.test(text)) data.letra = "B";
  else if (/\nC\s*\n\s*FACTURA/is.test(text)) data.letra = "C";
  else data.letra = "";

  data.strad = "";
  data[0] = 0.0;
  data.alquiler = 0;
  data.perce = 0;

  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  data["fecha proceso"] = `${pad(now.getDate())}/${pad(now.getMonth() + 1)}/${now.getFullYear()}`;

  return data;
}
