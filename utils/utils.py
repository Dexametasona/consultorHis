from collections import defaultdict
from datetime import datetime
import re
from tkinter import filedialog
from openpyxl import Workbook, load_workbook
import sys
from pathlib import Path


def getDniFromExcel(file_route):
    wb = load_workbook(file_route, read_only=True, data_only=True)
    ws = wb.active

    dnis = []
    errors = []

    for index_row, (value,) in enumerate(
        ws.iter_rows(min_col=1, max_col=1, values_only=True),
        start=1,
    ):
        if value is None:
            continue  # Ignora filas vacías

        text = str(value).strip()

        # Si Excel guardó el DNI como número, recupera ceros iniciales.
        if isinstance(value, int):
            text = f"{value:08d}"

        if re.fullmatch(r"\d{8}", text):
            dnis.append(text)
        else:
            errors.append(
                f"Fila {index_row}: debe contener un DNI de 8 dígitos."
            )

    wb.close()
    return dnis, errors


def export_excel(data, cpms):
    if not data:
        return None
    
    vaccineGroupByDniAndLab = defaultdict(lambda: defaultdict(list))
    patients = {}

    for dni, patient, fn, lab, date in data:
        if dni not in patients:
            patients[dni] = {
                "paciente": patient,
                "fn": fn,
            }

        # Una atención sin LAB también es válida.
        lab_key = str(lab).strip() if lab is not None else ""
        if not lab_key:
            lab_key = "SIN_LAB"

        if date:
            vaccineGroupByDniAndLab[dni][lab_key].append(date)
    # Identificar los LAB únicos, incluyendo SIN_LAB.
    labs = sorted({
        lab
        for group in vaccineGroupByDniAndLab.values()
        for lab in group
    })
    
     # Determinar cuántas columnas necesita cada LAB.
    columnsBySameLab = {
        lab: max(
            len(group.get(lab, []))
            for group in vaccineGroupByDniAndLab.values()
        )
        for lab in labs
    }
    
    output_route = filedialog.asksaveasfilename(
        title="Guardar resultados",
        defaultextension=".xlsx",
        filetypes=[("Archivo Excel", "*.xlsx")],
        initialfile="resultados_his.xlsx"
    )

    if not output_route:
        return None

    book = Workbook()
    sheet = book.active
    sheet.title = "Atenciones"
    
    # Crear cabeceras dinámicas.
    headers = ["DNI", "Paciente", "FN", "Edad"]
    for lab in labs:
        for number in range(columnsBySameLab[lab]):
            sufijo = "" if number == 0 else f"({number})"
            headers.append(f"{cpms}-{lab}{sufijo}")

    sheet.append(headers)
    
    for dni, datos in patients.items():
        row = [dni, datos["paciente"] or "", datos["fn"] or "", None]

        for lab in labs:
            dates = sorted(
                vaccineGroupByDniAndLab[dni].get(lab, []),
                key=sort_dates
            )

            amount = columnsBySameLab[lab]

            for number in range(amount):
                row.append(
                    dates[number]
                    if number < len(dates)
                    else ""
                )

        sheet.append(row)
        current_row = sheet.max_row
        sheet.cell(
            row=current_row,
            column=4,
            value=f'=IF(C{current_row}="","",DATEDIF(C{current_row},TODAY(),"Y"))'
        )


    sheet.freeze_panes = "E2"
    sheet.auto_filter.ref = sheet.dimensions

    
    
    book.save(output_route)

    return output_route

def sort_dates(fecha):
    if not fecha:
        return datetime.min

    texto = str(fecha).strip()

    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue

    return datetime.min

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path