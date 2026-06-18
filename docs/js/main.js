import { readPdfText, extractInvoiceData } from "./pdf-parser.js?v=4";
import { writeRowsToExcel } from "./excel-export.js";
import * as pdfjsLib from "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.mjs";
import ExcelJS from "https://cdn.jsdelivr.net/npm/exceljs@4.4.0/+esm";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.worker.mjs";

const pdfFiles = [];
let excelFile = null;

const pdfInput = document.getElementById("pdf-input");
const excelInput = document.getElementById("excel-input");
const pdfList = document.getElementById("pdf-list");
const pdfCount = document.getElementById("pdf-count");
const excelLabel = document.getElementById("excel-label");
const processBtn = document.getElementById("process-btn");
const statusEl = document.getElementById("status");
const toast = document.getElementById("toast");

function showToast(message, type = "info") {
  toast.textContent = message;
  toast.className = `toast visible ${type}`;
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => toast.classList.remove("visible"), 5000);
}

function updateStatus() {
  const n = pdfFiles.length;
  if (n === 0) statusEl.textContent = "Esperando archivos para procesar";
  else if (n === 1) statusEl.textContent = "1 factura cargada en tu navegador";
  else statusEl.textContent = `${n} facturas cargadas en tu navegador`;
  pdfCount.textContent = n === 0 ? "Sin archivos cargados" : `${n} archivo(s)`;
  processBtn.disabled = n === 0 || !excelFile;
}

function renderPdfList() {
  pdfList.innerHTML = "";
  if (pdfFiles.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Todavía no hay facturas. Seleccioná o arrastrá PDFs desde el panel izquierdo.";
    pdfList.appendChild(empty);
    return;
  }

  pdfFiles.forEach((file, index) => {
    const li = document.createElement("li");
    li.className = "pdf-item";

    const name = document.createElement("span");
    name.className = "pdf-name";
    name.textContent = file.name;
    name.title = file.name;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove-btn";
    remove.textContent = "✕";
    remove.title = "Quitar";
    remove.addEventListener("click", () => {
      pdfFiles.splice(index, 1);
      renderPdfList();
      updateStatus();
    });

    li.append(name, remove);
    pdfList.appendChild(li);
  });
}

function addPdfFiles(files) {
  for (const file of files) {
    if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
      if (!pdfFiles.some((f) => f.name === file.name && f.size === file.size)) {
        pdfFiles.push(file);
      }
    }
  }
  renderPdfList();
  updateStatus();
}

pdfInput.addEventListener("change", (e) => {
  addPdfFiles([...e.target.files]);
  pdfInput.value = "";
});

excelInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    excelFile = file;
    const label = file.name.length > 40 ? `…/${file.name.slice(-36)}` : file.name;
    excelLabel.textContent = label;
    excelLabel.title = file.name;
  }
  updateStatus();
});

document.getElementById("pdf-drop").addEventListener("dragover", (e) => {
  e.preventDefault();
  e.currentTarget.classList.add("dragover");
});

document.getElementById("pdf-drop").addEventListener("dragleave", (e) => {
  e.currentTarget.classList.remove("dragover");
});

document.getElementById("pdf-drop").addEventListener("drop", (e) => {
  e.preventDefault();
  e.currentTarget.classList.remove("dragover");
  addPdfFiles([...e.dataTransfer.files]);
});

processBtn.addEventListener("click", async () => {
  if (!pdfFiles.length || !excelFile) return;

  processBtn.disabled = true;
  processBtn.textContent = "Procesando en tu navegador…";
  statusEl.textContent = "Leyendo facturas PDF (sin enviar datos a internet)…";

  const extractedRows = [];
  const errors = [];

  try {
    for (const file of pdfFiles) {
      try {
        const buffer = await file.arrayBuffer();
        const text = await readPdfText(buffer, pdfjsLib);
        if (!text.trim()) {
          errors.push(`${file.name}: no se pudo leer texto del PDF.`);
          continue;
        }
        extractedRows.push(extractInvoiceData(text));
      } catch (err) {
        errors.push(`${file.name}: ${err.message || err}`);
      }
    }

    if (!extractedRows.length) {
      showToast("No se pudieron extraer datos de ningún PDF.", "error");
      statusEl.textContent = "Error en la extracción";
      return;
    }

    statusEl.textContent = "Armando el archivo Excel…";
    const templateBuffer = await excelFile.arrayBuffer();
    const outputBuffer = await writeRowsToExcel(templateBuffer, extractedRows, ExcelJS);

    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    const filename = `Liquidaciones_procesadas_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}.xlsx`;

    const blob = new Blob([outputBuffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    let msg = `Listo: ${extractedRows.length} factura(s) exportada(s) a tu descargas.`;
    if (errors.length) msg += ` ${errors.length} advertencia(s).`;
    showToast(msg, errors.length ? "warn" : "success");
    statusEl.textContent = `Completado · ${extractedRows.length} factura(s) procesada(s) localmente`;

    if (errors.length) console.warn("Advertencias:", errors);
  } catch (err) {
    showToast(`Error: ${err.message || err}`, "error");
    statusEl.textContent = "Error al procesar";
    console.error(err);
  } finally {
    processBtn.textContent = "Procesar facturas y descargar Excel";
    updateStatus();
  }
});

renderPdfList();
updateStatus();
