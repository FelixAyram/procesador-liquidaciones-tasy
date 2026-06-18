"""Esquema de columnas Excel Tasy."""

COLUMN_ORDER = [
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
]

AMOUNT_COLUMN_INDEXES = {5, 6, 7, 8, 9, 10, 11, 19}
DATE_COLUMN_INDEXES = {12, 13, 18, 21}
INTEGER_COLUMN_INDEXES = {4, 15, 17, 22, 23}


def row_to_values(row_data: dict) -> list:
    return [row_data.get(key, "") for key in COLUMN_ORDER]
