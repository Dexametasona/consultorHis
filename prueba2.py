import shutil
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from urllib.request import urlopen
import re
from openpyxl import Workbook, load_workbook
from datetime import datetime
from openpyxl.styles import Alignment

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


PUERTO_CDP = 9222
URL_CDP = f"http://127.0.0.1:{PUERTO_CDP}"
URL_HIS_MINSA = "websalud.minsa.gob.pe"


def buscar_chrome():
    chrome_en_path = shutil.which("chrome.exe")
    if chrome_en_path:
        return chrome_en_path

    rutas = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
    ]

    for ruta in rutas:
        if ruta.exists():
            return str(ruta)

    raise FileNotFoundError("No se encontró chrome.exe.")


class ConsultorHIS:
    def __init__(self, ventana):
        self.ventana = ventana
        self.archivo_excel = ""
        self.chrome_proceso = None
        self.playwright = None
        self.browser = None
        self.pagina_his = None
        self.dnis = None

        self.ventana.title("Consultor HIS-MINSA")
        self.ventana.geometry("600x300")
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

        tk.Label(ventana, text="Archivo Excel:").pack(anchor="w", padx=30, pady=(20, 4))

        fila_archivo = tk.Frame(ventana)
        fila_archivo.pack(fill="x", padx=30)

        self.input_file = tk.Entry(fila_archivo)
        self.input_file.pack(side="left", fill="x", expand=True)

        tk.Button(
            fila_archivo,
            text="Seleccionar",
            command=self.seleccionar_excel,
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            ventana,
            text="Código CPMS/CIE (mínimo 3 caracteres):",
        ).pack(anchor="w", padx=30, pady=(18, 4))

        self.input_codigo = tk.Entry(ventana, width=15)
        self.input_codigo.pack(anchor="w", padx=30)

        tk.Button(
            ventana,
            text="Abrir Chrome para iniciar sesión",
            command=self.abrir_chrome,
        ).pack(pady=(18, 5))

        tk.Button(
            ventana,
            text="Conectar y continuar",
            command=self.conectar_y_continuar,
        ).pack()

    def seleccionar_excel(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
        )
        if archivo:
            self.archivo_excel = archivo
            self.input_file.delete(0, tk.END)
            self.input_file.insert(0, archivo)

    def validar_interfaz(self):
        archivo = self.input_file.get().strip()
        codigo = self.input_codigo.get().strip()

        if not archivo:
            messagebox.showwarning("Falta archivo", "Selecciona primero un archivo Excel.")
            return None

        if not Path(archivo).is_file():
            messagebox.showwarning("Archivo inválido", "No se encontró el archivo seleccionado.")
            return None

        if len(codigo) < 3:
            messagebox.showwarning(
                "Código inválido",
                "El CPMS/CIE debe tener al menos 3 caracteres.",
            )
            return None

        return archivo, codigo

    def abrir_chrome(self):
        try:
            chrome = buscar_chrome()
            perfil = Path(tempfile.gettempdir()) / "chrome-playwright"
            perfil.mkdir(parents=True, exist_ok=True)

            self.chrome_proceso = subprocess.Popen([
                chrome,
                f"--remote-debugging-port={PUERTO_CDP}",
                f"--user-data-dir={perfil}",
                "https://websalud.minsa.gob.pe"
            ])

            messagebox.showinfo(
                "Chrome abierto",
                "Inicia sesión manualmente en HIS-MINSA con este Chrome "
                "y navega hasta la página que busca inmunizaciones. Luego pulsa "
                "«Conectar y continuar».",
            )
        except Exception as error:
            messagebox.showerror("No se pudo abrir Chrome", str(error))

    def localizar_pagina_his(self):
        if self.browser is None:
            return None

        for contexto in self.browser.contexts:
            for pagina in contexto.pages:
                campo = pagina.locator('input[name="confighistorialpacid"]')

                try:
                    campo.wait_for(state="visible", timeout=3000)
                    return pagina
                except PlaywrightTimeoutError:
                    continue
        return None

    def leer_dni_excel(self):
        wb = load_workbook(self.archivo_excel, read_only=True, data_only=True)
        ws = wb.active

        dnis = []
        errores = []

        for numero_fila, (valor,) in enumerate(
            ws.iter_rows(min_col=1, max_col=1, values_only=True),
            start=1,
        ):
            if valor is None:
                continue  # Ignora filas vacías

            texto = str(valor).strip()

            # Si Excel guardó el DNI como número, recupera ceros iniciales.
            if isinstance(valor, int):
                texto = f"{valor:08d}"

            if re.fullmatch(r"\d{8}", texto):
                dnis.append(texto)
            else:
                errores.append(
                    f"Fila {numero_fila}: debe contener un DNI de 8 dígitos."
                )

        wb.close()
        return dnis, errores
    
    def consultar_dni(self, dni, cpms):
        input_dni = self.pagina_his.locator('input[name="numdoc"]')

        with self.pagina_his.expect_response(
            lambda respuesta:
                "/hisminsa/his/his" in respuesta.url
                and "confighistorialpacid=1" in respuesta.url
        ) as respuesta_info:
            input_dni.fill(dni)

        respuesta = respuesta_info.value
        datos = respuesta.json()

        paciente = self.pagina_his.locator(
            'input[name="paciente"]'
        ).input_value()

        fecha_nacimiento = self.pagina_his.locator(
            'input[name="fecnacimiento"]'
        ).input_value()

        filas = []

        for item in datos.get("items", []):
            codigo_encontrado = str(item.get("coditem", "")).strip()

            if codigo_encontrado == cpms:
                filas.append({
                    "dni": dni,
                    "paciente": paciente,
                    "FN": fecha_nacimiento,
                    "cpms": codigo_encontrado,
                    "lab": item.get("valorlab"),
                    "fecha_atencion": item.get("periodo"),
                })
        if not filas:
            filas.append({
                "dni": dni,
                "paciente": paciente,
                "FN": fecha_nacimiento,
                "cpms": "",
                "lab": "",
                "fecha_atencion": "",
                            })
        return filas

    @staticmethod
    def guardar_resultados_agrupados(resultados, cpms, ruta_salida):
        # Obtiene los valores únicos de LAB, ignorando los vacíos.
        labs = sorted({
            str(fila.get("lab", "")).strip()
            for fila in resultados
            if fila.get("lab")
        })

        # Agrupa todas las consultas de cada paciente por DNI.
        pacientes = {}

        for fila in resultados:
            dni = str(fila.get("dni", "")).strip()
            if not dni:
                continue

            paciente = pacientes.setdefault(dni, {
                "dni": dni,
                "paciente": fila.get("paciente", ""),
                "FN": fila.get("FN", ""),
                "fechas_por_lab": {},
            })

            lab = str(fila.get("lab", "")).strip()
            fecha = fila.get("fecha_atencion")

            if lab and fecha:
                fechas = paciente["fechas_por_lab"].setdefault(lab, [])

                # Evita repetir la misma fecha para el mismo paciente y LAB.
                fecha_texto = str(fecha).strip()
                if fecha_texto not in fechas:
                    fechas.append(fecha_texto)

        wb = Workbook()
        ws = wb.active

        # Excel limita los nombres de hoja a 31 caracteres y prohíbe estos signos.
        nombre_hoja = str(cpms)
        for caracter in r'\/?*[]:':
            nombre_hoja = nombre_hoja.replace(caracter, "_")
        ws.title = nombre_hoja[:31] or "CPMS"

        ws.append([
            "DNI",
            "Paciente",
            "Fecha de nacimiento",
            *labs,
        ])

        for paciente in pacientes.values():
            fila_excel = [
                paciente["dni"],
                paciente["paciente"],
                paciente["FN"],
            ]

            for lab in labs:
                fechas = paciente["fechas_por_lab"].get(lab, [])
                # Si hay varias administraciones del mismo LAB, van en líneas separadas.
                fila_excel.append("\n".join(fechas))

            ws.append(fila_excel)

        # Permite ver todas las fechas cuando una celda contiene varias.
        for fila in ws.iter_rows(min_row=2):
            for celda in fila:
                celda.alignment = Alignment(vertical="top", wrap_text=True)

        wb.save(ruta_salida)
    
    def procesar_excel(self, cpms):
        dnis, errores = self.leer_dni_excel()

        if errores:
            messagebox.showwarning(
                "Revisa el Excel",
                "\n".join(errores[:10]),
            )

        if not dnis:
            messagebox.showwarning(
                "Sin DNI",
                "No se encontraron DNI válidos en la primera columna.",
            )
            return

        resultados = []
        errores_consulta = []

        for posicion, dni in enumerate(dnis, start=1):
            try:
                filas = self.consultar_dni(dni, cpms)
                resultados.extend(filas)
                print(f"{posicion}/{len(dnis)}: DNI consultado.")
            except Exception as error:
                errores_consulta.append(f"{dni}: {error}")

        ruta_salida = Path(self.archivo_excel).with_name(
            f"{Path(self.archivo_excel).stem}_resultado.xlsx"
        )

        self.guardar_resultados_agrupados(
            resultados=resultados,
            cpms=cpms,
            ruta_salida=ruta_salida,
        )

        mensaje = (
            f"Consultas terminadas.\n"
            f"Coincidencias encontradas: {len(resultados)}\n"
            f"Archivo guardado en:\n{ruta_salida}"
        )

        if errores_consulta:
            mensaje += (
                f"\n\nConsultas con error: {len(errores_consulta)}"
                f"\n{chr(10).join(errores_consulta[:5])}"
            )

        messagebox.showinfo("Proceso terminado", mensaje)
    
    def conectar_y_continuar(self):
        datos = self.validar_interfaz()
        if datos is None:
            return

        archivo, codigo = datos

        try:
            # Comprueba que Chrome ya haya iniciado el servicio CDP.
            with urlopen(f"{URL_CDP}/json/version", timeout=2):
                pass

            if self.playwright is None:
                self.playwright = sync_playwright().start()

            if self.browser is None:
                self.browser = self.playwright.chromium.connect_over_cdp(URL_CDP)

            self.pagina_his = self.localizar_pagina_his()
            
            self.procesar_excel(codigo)
                 
            if self.pagina_his is None:
                messagebox.showwarning(
                    "Falta HIS-MINSA",
                    "Chrome está disponible, pero no se encontró una pestaña "
                    "de HIS-MINSA adecuada. Navega hasta allí y vuelve a conectar.",
                )
                return

            messagebox.showinfo(
                "Conexión lista",
                f"Playwright encontró HIS-MINSA.\n\n"
                f"Excel: {archivo}\nCódigo: {codigo}\n\n"
            )

        except Exception as error:
            messagebox.showerror(
                "No se pudo conectar",
                "Verifica que Chrome se haya abierto con el perfil dedicado "
                "y que siga ejecutándose.\n\n"
                f"Detalle: {error}",
            )
            
        
    def cerrar(self):
        # Detiene el cliente Playwright al cerrar la aplicación.
        if self.playwright is not None:
            self.playwright.stop()

        self.ventana.destroy()


ventana = tk.Tk()
app = ConsultorHIS(ventana)
ventana.mainloop()