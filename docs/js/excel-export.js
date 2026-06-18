/** Exportación Excel Tasy — versión navegador (ExcelJS). */

const COLUMN_ORDER = [
  "strad",
  "a y n",
  "cuit",
  0,
  "exento",
  "gr10,5",
  "gr 21",
  "iva10,5 ",
  "iva 21",
  "total",
  "alquiler",
  "fecha proceso",
  "fecha pago",
  "cpte",
  "punto",
  "letra",
  "nro",
  "fecha",
  "perce",
  "cae",
  "fecha cae",
  "anio_periodo",
  "mes_periodo",
  "sigla_clinica",
];

const AMOUNT_COLUMN_INDEXES = new Set([5, 6, 7, 8, 9, 10, 11, 19]);
const DATE_COLUMN_INDEXES = new Set([12, 13, 18, 21]);
const INTEGER_COLUMN_INDEXES = new Set([4, 15, 17, 22, 23]);

const HEADER_COLOR = "1E1B4B";
const THIN_BORDER = {
  top: { style: "thin", color: { argb: "FFCBD5E1" } },
  left: { style: "thin", color: { argb: "FFCBD5E1" } },
  bottom: { style: "thin", color: { argb: "FFCBD5E1" } },
  right: { style: "thin", color: { argb: "FFCBD5E1" } },
};

function rowToValues(rowData) {
  return COLUMN_ORDER.map((key) => {
    const v = rowData[key];
    return v === undefined || v === null ? "" : v;
  });
}

function nextAppendRow(worksheet) {
  if (worksheet.rowCount <= 1) return 2;

  let lastWithData = 1;
  const maxCol = Math.max(worksheet.columnCount, COLUMN_ORDER.length, 1);

  for (let rowIdx = 2; rowIdx <= worksheet.rowCount; rowIdx++) {
    const row = worksheet.getRow(rowIdx);
    let hasData = false;
    for (let col = 1; col <= maxCol; col++) {
      const val = row.getCell(col).value;
      if (val !== null && val !== undefined && val !== "") {
        hasData = true;
        break;
      }
    }
    if (hasData) lastWithData = rowIdx;
  }
  return lastWithData + 1;
}

function cellDisplayLength(value) {
  if (value === null || value === undefined) return 0;
  if (typeof value === "number") {
    if (Number.isInteger(value)) {
      return value.toLocaleString("es-AR").length;
    }
    return value.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).length;
  }
  return String(value).length;
}

export function formatExcelWorksheet(worksheet) {
  const maxRow = worksheet.rowCount;
  const maxCol = Math.max(worksheet.columnCount, COLUMN_ORDER.length);

  for (let rowIdx = 1; rowIdx <= maxRow; rowIdx++) {
    const row = worksheet.getRow(rowIdx);
    row.height = rowIdx === 1 ? 36 : row.height;

    for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
      const cell = row.getCell(colIdx);
      cell.border = THIN_BORDER;
      cell.font = { name: "Segoe UI", size: 11, color: { argb: "FF1E293B" } };

      if (rowIdx === 1) {
        cell.font = { name: "Segoe UI", bold: true, size: 11, color: { argb: "FFFFFFFF" } };
        cell.fill = {
          type: "pattern",
          pattern: "solid",
          fgColor: { argb: "FF" + HEADER_COLOR },
        };
        cell.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
      } else {
        if (rowIdx % 2 === 0) {
          cell.fill = {
            type: "pattern",
            pattern: "solid",
            fgColor: { argb: "FFF8FAFC" },
          };
        }
        if (AMOUNT_COLUMN_INDEXES.has(colIdx)) {
          cell.numFmt = "#,##0.00";
          cell.alignment = { horizontal: "right", vertical: "middle" };
        } else if (DATE_COLUMN_INDEXES.has(colIdx)) {
          cell.alignment = { horizontal: "center", vertical: "middle" };
        } else if (INTEGER_COLUMN_INDEXES.has(colIdx)) {
          cell.alignment = { horizontal: "center", vertical: "middle" };
        } else {
          cell.alignment = { horizontal: "left", vertical: "middle" };
        }
      }
    }
  }

  worksheet.views = [{ state: "frozen", ySplit: 1, activeCell: "A2" }];

  if (maxRow >= 1 && maxCol >= 1) {
    worksheet.autoFilter = {
      from: { row: 1, column: 1 },
      to: { row: maxRow, column: maxCol },
    };
  }

  for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
    let maxLength = 0;
    for (let rowIdx = 1; rowIdx <= maxRow; rowIdx++) {
      maxLength = Math.max(maxLength, cellDisplayLength(worksheet.getRow(rowIdx).getCell(colIdx).value));
    }
    const headerVal = worksheet.getRow(1).getCell(colIdx).value;
    const headerLen = headerVal != null ? String(headerVal).length : 8;
    let width = Math.max(maxLength, headerLen) + 2;

    if (AMOUNT_COLUMN_INDEXES.has(colIdx)) {
      width = Math.max(width, 14);
    } else if (colIdx === 2 || colIdx === 24) {
      width = Math.min(Math.max(width, 20), 38);
    } else {
      width = Math.min(width, 30);
    }

    worksheet.getColumn(colIdx).width = width;
  }
}

export async function writeRowsToExcel(templateBuffer, rows, ExcelJS) {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(templateBuffer);
  const worksheet = workbook.worksheets[0];

  const startRow = nextAppendRow(worksheet);
  rows.forEach((rowData, offset) => {
    const values = rowToValues(rowData);
    const row = worksheet.getRow(startRow + offset);
    values.forEach((value, colIdx) => {
      row.getCell(colIdx + 1).value = value;
    });
    row.commit();
  });

  formatExcelWorksheet(worksheet);
  return workbook.xlsx.writeBuffer();
}
