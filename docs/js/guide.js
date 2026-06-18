/** Guía visual paso a paso: PDF → Plantilla → Procesar. */

const STEPS = ["pdf", "excel", "process"];

export function updateGuideStep(pdfCount, hasExcel, isProcessing = false) {
  let step = 0;
  if (pdfCount > 0) step = 1;
  if (pdfCount > 0 && hasExcel) step = 2;
  if (isProcessing) step = 2;

  const guide = document.getElementById("guide");
  if (!guide) return;

  guide.style.setProperty("--step", String(step));
  guide.dataset.step = STEPS[step];

  document.querySelectorAll(".guide-step").forEach((el, i) => {
    el.classList.toggle("active", i === step);
    el.classList.toggle("done", i < step);
  });

  const pdfCard = document.getElementById("step-pdf-card");
  const excelCard = document.getElementById("step-excel-card");
  const processBtn = document.getElementById("process-btn");

  pdfCard?.classList.toggle("guide-highlight", step === 0);
  excelCard?.classList.toggle("guide-highlight", step === 1);
  processBtn?.classList.toggle("guide-highlight", step === 2 && !isProcessing);
  processBtn?.classList.toggle("guide-ready", step === 2 && !isProcessing);
}
