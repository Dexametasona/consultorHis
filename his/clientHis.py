from pathlib import Path
import shutil
import subprocess
import tempfile
from tkinter import messagebox
from urllib.request import urlopen
from config import PUERTO_CDP, URL_CDP
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

class ClientHIS: 
    def __init__(self):
        self.browser = None
        self.playwright = None
        self.hisPage = None
        self.last_error =  None
        
    def searchChromeApp(self):
        chrome_path = shutil.which("chrome.exe")
        if chrome_path:
            return chrome_path

        routes = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
        ]

        for route in routes:
            if route.exists():
                return str(route)

        raise FileNotFoundError("No se encontró chrome.exe.")

    def openChrome(self):
        try:
            chrome = self.searchChromeApp()
            perfil = Path(tempfile.gettempdir()) / "chrome-playwright"
            perfil.mkdir(parents=True, exist_ok=True)

            subprocess.Popen([
                chrome,
                f"--remote-debugging-port={PUERTO_CDP}",
                f"--user-data-dir={perfil}",
                "https://websalud.minsa.gob.pe"
            ])
            
        except Exception as error:
            messagebox.showerror("No se pudo abrir Chrome", str(error))
        
    def connectChrome(self, show_messages=True):
        self.last_error = None
        try:
            # Comprueba que Chrome ya haya iniciado el servicio CDP.
            with urlopen(f"{URL_CDP}/json/version", timeout=2):
                pass

            if self.playwright is None:
                self.playwright = sync_playwright().start()

            if self.browser is None:
                self.browser = self.playwright.chromium.connect_over_cdp(URL_CDP)

            self.hisPage = self.search_HisPage()
            
            if self.hisPage is None:
                self.last_error = ( "Chrome está disponible, pero no se encontró una pestaña de HIS-MINSA adecuada.")

                if show_messages:
                    messagebox.showwarning(
                        "Falta HIS-MINSA",
                        self.last_error
                    )
                return None
            self.setVaccineRequestLimit()
            return self.hisPage
            
        except Exception as error:
            self.last_error = str(error)
            if show_messages:
                messagebox.showerror(
                    "No se pudo conectar",
                    "Verifica que Chrome esté abierto y que siga "
                    f"ejecutándose.\n\nDetalle: {error}",
                )

            return None      
            
    def search_HisPage(self):
        if self.browser is None:
            return None

        for context in self.browser.contexts:
            for page in context.pages:
                operationType = page.locator('input[name="confighistorialpacid"]')

                try:
                    operationType.wait_for(state="visible", timeout=3000)
                    return page
                except PlaywrightTimeoutError:
                    continue
        return None

    def vaccinesByDni(self, dni):
        inputDNI = self.hisPage.locator('input[name="numdoc"]')
        with self.hisPage.expect_response(
            lambda req:
                "/hisminsa/his/his" in req.url
                and "confighistorialpacid=1" in req.url
        ) as res:
            inputDNI.fill(dni)

        dataJson = res.value
        data = dataJson.json()

        patient = self.hisPage.locator(
            'input[name="paciente"]'
        ).input_value()

        birthdate = self.hisPage.locator(
            'input[name="fecnacimiento"]'
        ).input_value()

        patientVaccines = []

        for item in data.get("items", []):
            patientVaccines.append({
                "cpms": item.get("coditem"),
                "lab": item.get("valorlab"),
                "date": item.get("periodo"),
                })
            
        return {
            "dni":dni,
            "paciente":patient,
            "FN":birthdate,
            "vaccines":patientVaccines
        }
    
    def closePlaywright(self):
        try:
            if self.playwright is not None:
                self.playwright.stop()
        finally:
            self.playwright = None
            self.browser = None
            self.hisPage = None
    
    def setVaccineRequestLimit(self):
        def modifyRequest(route):
            request = route.request
            url = request.url

            if (
                "/hisminsa/his/his" in url
                and "confighistorialpacid=1" in url
                and "C=HISTORIALATENCIONES" in url
            ):
                from urllib.parse import (
                    urlsplit,
                    parse_qsl,
                    urlencode,
                    urlunsplit,
                )

                parts = urlsplit(url)
                params = dict(parse_qsl(parts.query))
                params["limit"] = "100"

                new_url = urlunsplit((
                    parts.scheme,
                    parts.netloc,
                    parts.path,
                    urlencode(params),
                    parts.fragment,
                ))

                route.continue_(url=new_url)
            else:
                route.continue_()

        self.hisPage.route(
            "**/hisminsa/his/his**",
            modifyRequest,
        )