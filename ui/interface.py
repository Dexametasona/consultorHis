from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from database.database import  getQueryList, delete_query, getPatientsAndVaccinesByQuery
from services.query_service import getVaccinesByAllDni
from ui.styles import configStyle
from utils.utils import export_excel, resource_path
import threading
import queue

def initInterface(clientHis):
    result_queue = queue.Queue()
    worker_running = False
    def selectQuery(id_query, file):
        queryID_selected.set(id_query)
        query_selected.set(f"Consulta: {file}")
        
    def connectAndExecute():
        nonlocal worker_running
        if worker_running:
            return
        
        origin_route = interfaceValidator(input_file)
        if origin_route is None:
            return
        
        worker_running = True
        btn_connect.config(state="disabled")
        loading_label.config(text="Conectando y consultando HIS-MINSA...")
        loading_label.pack(anchor="w")
        loading_bar.pack(fill="x", pady=(4, 0))
        loading_bar["value"] = 0
        progress_label.config(text=f"Preparando consulta")
        progress_label.pack(anchor="e")
        
        def update_progress(actual, total):
            progress = actual / total * 100 if total else 0

            loading_bar["value"] = progress
            progress_label.config(
                text=f"{actual}/{total} DNI consultados"
            )
        
        def worker():
            try:
                page = clientHis.connectChrome(show_messages=False)
                if page is None:
                    raise RuntimeError(getattr(clientHis, "last_error", None)
                    or "No se pudo conectar con HIS-MINSA."
                )
                    
                vaccines = getVaccinesByAllDni(
                    origin_route, 
                    clientHis, 
                    lambda current, total: update_progress(current, total))
                result_queue.put(("success", vaccines))
                
            except Exception as error:
                result_queue.put(('error', str(error)))
                
            finally:
                clientHis.closePlaywright()
                
        threading.Thread(target=worker, daemon=True,).start()
        check_worker()
            
    def check_worker():
        nonlocal worker_running
        while True:
            try:
                status, result = result_queue.get_nowait()

            except queue.Empty:
                break;

            if status == "progress":
                actual, total = result
                progress_label.config(
                    text=f"{actual}/{total} DNI consultados"
                )
            elif status == "success":
                worker_running = False
                loading_bar.stop()
                loading_bar.pack_forget()
                loading_label.pack_forget()
                loading_container.pack_forget()
                btn_connect.config(state="normal")
                
                messagebox.showinfo(
                "Proceso finalizado",
                f"Consulta ID: {result['queryId']}\n"
                f"DNI procesados correctamente: {result['success']}\n"
                f"Errores: {result['errors']}\n"
                f"Detalles del error: {result['error_detail']}",
                parent=root,
            )

            elif status == "error":
                messagebox.showerror(
                    "Error en el proceso",
                    result,
                    parent=root,
                )
                return
            
        if worker_running:
            root.after(200, check_worker)
        
    def initExport_excel():
        queryID = queryID_selected.get()
        cpms = input_codigo.get().strip()

        if queryID == 0:
            messagebox.showwarning(
                "Falta consulta",
                "Primero selecciona una consulta del historial."
            )
            return
        if len(cpms) < 3:
            messagebox.showwarning(
                "Código inválido",
                "Ingresa al menos 3 caracteres."
            )
            return

        vaccinesByPatients = getPatientsAndVaccinesByQuery(queryID, cpms)
        if not vaccinesByPatients:
            messagebox.showinfo(
                "Sin resultados",
                "No se encontraron pacientes en esta consulta?."
            )
            return

        output_route = export_excel(vaccinesByPatients, cpms, query_selected.get())
        if output_route:
            messagebox.showinfo(
                "Exportación completada",
                f"Se exportaron {len(vaccinesByPatients)} atenciones.\n\n{output_route}"
            )

    #definimos la raiz de la interfaz
    root = tk.Tk()
    root.title("Consultor HIS-MINSA")
    root.geometry("600x398")
    root.minsize(600,398)
    root.protocol("WM_DELETE_WINDOW",     
                  lambda: close(root, lambda:worker_running))
    root.iconbitmap(str(resource_path("assets/icono.ico")))
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)

    configStyle(root)

    main_container = ttk.Frame(root, style="App.TFrame")
    main_container.grid(
        row=0,
        column=0,
        sticky="nsew",
        )
    
    #Interfaz de la conexión a chrome y el archivo de origen
    getData_container = ttk.LabelFrame(
        main_container, 
        text="Obtener datos", 
        style="Card.TLabelframe", 
        padding=(8,7)
        )
    getData_container.pack(fill="x")

    ttk.Label(
        getData_container, 
        text="Archivo Excel:",  
        style="App.TLabel",
        font=("Segoe UI", 10, "bold")
        ).pack(anchor='w', pady=(0, 6))
    
    ttk.Label(
        getData_container,
        text="Selecciona el archivo que contiene la lista de DNI.",
        style="Muted.TLabel",
    ).pack(anchor="w", pady=(0, 10))

    file_entry = ttk.Frame(getData_container, style='App.TFrame')
    file_entry.pack(fill="x")
    
    input_file = ttk.Entry(file_entry, style="App.TEntry")
    input_file.pack(side="left", fill="x", expand=True, ipady=1)

    ttk.Button(
        file_entry,
        text="Examinar...",
        style='Secondary.TButton',
        command= lambda: loadExcel(input_file),
    ).pack(side="left", padx=(8, 0))
    
    btn_container = ttk.Frame(getData_container, style='Card.TLabelframe.Label')
    btn_container.pack(pady=(16, 4), fill="x")
    btn_container.grid_columnconfigure(0, weight=1)
    btn_container.grid_columnconfigure(1, weight=1)

    ttk.Button(
        btn_container,
        text="Abrir Chrome",
        command=clientHis.openChrome,
        style='Secondary.TButton' 
    ).grid(column=0, row=0, padx=(0,6), sticky='ew')
    
    btn_connect = ttk.Button(
        btn_container,
        text="Conectar y continuar",
        command=connectAndExecute,
        style='Primary.TButton' 
    )
    btn_connect.grid(row=0, column=1, sticky="ew", padx=(6, 0))
    
    # interfaz del loader
    loading_container = ttk.Frame(getData_container, style='App.TFrame')
    loading_container.pack(fill="x", padx=10, pady=(0, 8))

    loading_label = ttk.Label(loading_container, text="", style='App.TLabel')
    loading_bar = ttk.Progressbar(
        loading_container, 
        mode="determinate", 
        length=250,
        maximum=100
        )
    progress_label = ttk.Label(loading_container, text="0/0 DNI consultados", style='Muted.TLabel')
    
    #interfaz del procesamiento de la informacion
    filters_container = ttk.LabelFrame(main_container, text='Procesar Información', style='Card.TLabelframe')
    filters_container.pack(fill='x', pady=(8,0), ipady=4)
    
    query_container = ttk.Frame(filters_container, style="Card.TLabelframe.Label")
    query_container.pack(fill='x', padx=8, pady=(8,0))
    query_selected = tk.StringVar(value='Ninguna')
    queryID_selected = tk.IntVar(value=0)
        
    ttk.Button(query_container, 
              text='Seleccionar consulta', 
              command=lambda: queryListWindow(query_container, selectQuery),
              style='Secondary.TButton'
              ).grid(column=1, row=0)
    ttk.Label(query_container, 
              textvariable=query_selected,
              style='Card.TLabelframe.Label'
              ).grid(column=2, row=0, padx=8)
    
    cpms_container = ttk.Frame(filters_container, style='Card.TLabelframe.Label')
    cpms_container.pack(padx=10, anchor='w')
    
    ttk.Label(
        cpms_container,
        text="Código CPMS/CIE (mínimo 3 caracteres):",
        style='Card.TLabelframe.Label'
    ).pack(pady=(16, 4))

    input_codigo = ttk.Entry(cpms_container, width=15, style='App.TEntry')
    input_codigo.pack(anchor="w")
    
    ttk.Button(filters_container, 
              text="Exportar",
              command=initExport_excel,
              style='Primary.TButton'
              ).pack(ipadx=8)

    # -----footer-----
    footer = tk.Frame(root)
    footer.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=10
    )
    tk.Label(
        footer,
        text="Desarrollado por Alexander Machicado G. 2026",
        font=("Segoe UI", 8),
        fg="gray"
    ).pack(side="right")    
    
    return root

def queryListWindow(container, when_select):
    def load():
        target = queryList.curselection()

        if not target:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona una consulta del historial."
            )
            return

        index = target[0]
        id_query = idsQuery[index]
        when_select(id_query, filesQuery[index])
        query_window.destroy()
        
    def delete():
        target = queryList.curselection()
        
        if not target:  
            messagebox.showwarning(
                "Sin selección",
                "Selecciona una consulta del historial."
            )
            return
        index = target[0]
        id_query = idsQuery[index]
        try:
            state = delete_query(queryId=id_query)
            if state:
                messagebox.showinfo('Operación exitosa', f"Se elimino la consulta con id: {id_query}, y sus vacunas asociadas.")
            else:
                messagebox.showinfo("No hay vacunas asociadas",f"Se elimino la consulta con id: {id_query}")        
        except Exception as error:
            messagebox.showerror(
                f"Error al eliminar consulta con ID: {id_query}", 
                str(error))
        finally:
            query_window.destroy()
    
    def closeWindow():
        query_window.grab_release()
        query_window.destroy()  
    
    query_window = tk.Toplevel(container)
    query_window.title('Seleccione la consulta')
    query_window.geometry("600x200")
    query_window.transient(container)
    query_window.grab_set()
    query_window.protocol("WM_DELETE_WINDOW", closeWindow)
    
    queryList = tk.Listbox(query_window, width=60)
    queryList.pack(side="left", fill='both', expand=True, padx=2, pady=2)
    
    scrollBar = tk.Scrollbar(
        queryList,
        orient='vertical', 
        command=queryList.yview)
    scrollBar.pack(side='right', fill="y")
    queryList.config(yscrollcommand=scrollBar.set)
    
    queries = getQueryList()
    idsQuery = []
    filesQuery = []
    
    for id, date, file, *_ in queries:
        text = f"  ID {id} | {date} | {file}"
        queryList.insert(tk.END, text)
        idsQuery.append(id)
        filesQuery.append(Path(file).name)
              
    
    btn_container = tk.Frame(query_window)
    btn_container.pack(side='right', padx=4)
    
    tk.Button(btn_container, 
              anchor='w', 
              text='Cargar',
              command=load
              ).grid(row=0, sticky='ew', pady=4)
    tk.Button(btn_container, 
              anchor='w', 
              text='Eliminar',
              command=delete
              ).grid(row=1, sticky='ew', pady=4)
    tk.Button(btn_container, 
              anchor='w', 
              text='Cancelar',
              command=closeWindow
              ).grid(row=2, sticky='ew', pady=4)
    
def loadExcel(input):
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
    )
    if archivo:
        input.delete(0, tk.END)
        input.insert(0, archivo)
        
def interfaceValidator(input):
    file = input.get().strip()

    if not file:
        messagebox.showwarning("Falta archivo", "Selecciona primero un archivo Excel.")
        return None

    if not Path(file).is_file():
        messagebox.showwarning("Archivo inválido", "No se encontró el archivo seleccionado.")
        return None

    return file
    
def close(root, is_running):
    if is_running():
        messagebox.showwarning(
            "Proceso en ejecución",
            "Espera a que termine la consulta antes de cerrar.",
            parent=root,
        )
        return
    root.destroy()
    