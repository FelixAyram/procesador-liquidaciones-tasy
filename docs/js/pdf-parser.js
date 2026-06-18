/** Lectura y extracción de datos de facturas PDF (AFIP) — versión navegador. */

const Y_TOLERANCE = 5;
const DATE_RE = /(\d{2}\/\d{2}\/\d{4})/;

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

/** Une etiquetas AFIP que pdf.js suele partir en varias líneas. */
export function normalizeAfipText(text) {
  return text
    .replace(/Comp\.\s*\n\s*Nro:/gi, "Comp. Nro:")
    .replace(/Punto de Venta:\s*\n\s*/gi, "Punto de Venta: ")
    .replace(/Raz[oó]n Social:\s*\n\s*/gi, "Razón Social: ");
}

function cleanPersonName(name) {
  return name
    .replace(/\s+Fecha de Emisi[oó]n:.*$/i, "")
    .replace(/\s+\d{2}\/\d{2}\/\d{4}\s*$/, "")
    .trim();
}

function extractRazonSocial(text) {
  let match = text.match(
    /Raz[oó]n Social:\s*(.+?)(?:\s+Fecha de Emisi[oó]n:)/is
  );
  if (match) return cleanPersonName(match[1]);

  match = text.match(/Raz[oó]n Social:\s*([^\n]+)/i);
  if (match) return cleanPersonName(match[1]);

  match = text.match(/FACTURA\s*\n\s*([A-ZÁÉÍÓÚÑ][^\n]+)/i);
  if (match) {
    const name = cleanPersonName(match[1].trim());
    if (!/^(COD\.|Punto de Venta:)/i.test(name)) return name;
  }

  return "";
}

function extractIssuerCuit(text) {
  // CUIT en la línea siguiente a Razón Social (layout pdf.js)
  let match = text.match(/Raz[oó]n Social:[^\n]*\n\s*CUIT:\s*(\d{11})/i);
  if (match) return match[1];

  // Primer CUIT del encabezado del emisor (antes del bloque cliente)
  const headerEnd = text.search(/Per[ií]odo Facturado Desde/i);
  const top = headerEnd > 0 ? text.slice(0, headerEnd) : text;
  match = top.match(/CUIT:\s*(\d{11})/i);
  if (match) return match[1];

  // CUIT en la misma línea que Domicilio Comercial del emisor
  match = text.match(/Domicilio Comercial:[^\n]*CUIT:\s*(\d{11})/i);
  return match ? match[1] : "";
}

function extractFechaEmision(text, rawNameLine) {
  let match = text.match(/Fecha de Emisi[oó]n:\s*(\d{2}\/\d{2}\/\d{4})/i);
  if (match) return match[1];

  if (rawNameLine) {
    match = rawNameLine.match(DATE_RE);
    if (match) return match[1];
  }

  match = text.match(/Punto de Venta:[^\n]{0,120}(\d{2}\/\d{2}\/\d{4})/i);
  if (match) return match[1];

  const headerEnd = text.search(/Per[ií]odo Facturado Desde/i);
  const top = headerEnd > 0 ? text.slice(0, headerEnd) : text.slice(0, 1200);
  match = top.match(/(\d{2}\/\d{2}\/\d{4})/);
  return match ? match[1] : "";
}

function extractLetra(text, cpte) {
  const patterns = [
    /\b(A|B|C)\s+FACTURA\b/i,
    /(?:^|\n)\s*(A|B|C)\s*\n\s*FACTURA/im,
    /FACTURA\s+(A|B|C)\b/i,
  ];
  for (const pattern of patterns) {
    const m = text.match(pattern);
    if (m) return m[1].toUpperCase();
  }

  const codMap = { "01": "A", "06": "B", "11": "C" };
  return codMap[cpte] || "";
}

function extractPuntoNro(text) {
  let match = text.match(/Punto de Venta:\s*(\d+)\s+Comp\.\s*Nro:\s*(\d+)/i);
  if (match) return { punto: match[1], nro: match[2] };

  match = text.match(/Punto de Venta:\s*(\d+)/i);
  const punto = match ? match[1] : "";

  match = text.match(/Comp\.\s*Nro:\s*(\d+)/i);
  if (!match) match = text.match(/(?:^|\s)Nro:\s*(\d+)/im);
  const nro = match ? match[1] : "";

  return { punto, nro };
}

/** Agrupa items de pdf.js en líneas (similar a pdfplumber). */
export function groupTextItemsIntoLines(items) {
  const lineMap = new Map();
  for (const item of items) {
    const str = item.str;
    if (!str || !str.trim()) continue;
    const y = Math.round(item.transform[5] / Y_TOLERANCE) * Y_TOLERANCE;
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
  return normalizeAfipText(parts.join("\n"));
}

export function extractInvoiceData(rawText) {
  const text = normalizeAfipText(extractFirstInvoiceText(rawText));
  const data = {};

  const rawNameLine = (text.match(/Raz[oó]n Social:\s*([^\n]+)/i) || [])[1] || "";

  data["a y n"] = extractRazonSocial(text);
  data.cuit = extractIssuerCuit(text);

  let match = text.match(/Importe Exento:\s*\$?\s*([\d.,]+)/i);
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

  data.fecha = extractFechaEmision(text, rawNameLine);

  match = text.match(/Fecha de Vto\. para el pago:\s*(\d{2}\/\d{2}\/\d{4})/i);
  data["fecha pago"] = match ? match[1] : "";

  const { punto, nro } = extractPuntoNro(text);
  data.punto = punto;
  data.nro = nro;

  match = text.match(/COD\.\s*(\d+)/i);
  data.cpte = match ? match[1] : "";

  match = text.match(/CAE N[°º]:\s*(\d+)/i);
  data.cae = match ? match[1] : "";

  match = text.match(/Fecha de Vto\. de CAE:\s*(\d{2}\/\d{2}\/\d{4})/i);
  data["fecha cae"] = match ? match[1] : "";

  match = text.match(/Per[ií]odo Facturado Desde:\s*(\d{2}\/\d{2}\/\d{4})/i);
  if (match) {
    const [, m, y] = match[1].split("/").map(Number);
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

  data.letra = extractLetra(text, data.cpte);

  data.strad = "";
  data[0] = 0.0;
  data.alquiler = 0;
  data.perce = 0;

  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  data["fecha proceso"] = `${pad(now.getDate())}/${pad(now.getMonth() + 1)}/${now.getFullYear()}`;

  return data;
}
