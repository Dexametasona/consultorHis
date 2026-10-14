from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from database.database import  getQueryList, delete_query, getPatientsAndVaccinesByQuery
from services.query_service import getVaccinesByAllDni
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
        loading_bar.start(10)
        
        def worker():
            try:
                page = clientHis.connectChrome(show_messages=False)
                if page is None:
                    raise RuntimeError(getattr(clientHis, "last_error", None)
                    or "No se pudo conectar con HIS-MINSA."
                )
                    
                vaccines = getVaccinesByAllDni(origin_route, clientHis)
                result_queue.put(("success", vaccines))
            
            except Exception as error:
                result_queue.put(('error', str(error)))
            finally:
                clientHis.closePlaywright()
                
        threading.Thread(target=worker, daemon=True,).start()
        check_worker()
            
    def check_worker():
        nonlocal worker_running
        try:
            status, result = result_queue.get_nowait()

        except queue.Empty:
            root.after(500, check_worker)
            return

        worker_running = False
        loading_bar.stop()
        loading_bar.pack_forget()
        loading_label.pack_forget()

        btn_connect.config(state="normal")

        if status == "error":
            messagebox.showerror(
                "Error en el proceso",
                result,
                parent=root,
            )
            return

        messagebox.showinfo(
            "Proceso finalizado",
            f"Consulta ID: {result['queryId']}\n"
            f"DNI procesados correctamente: {result['success']}\n"
            f"Errores: {result['errors']}\n"
            f"Detalles del error: {result['error_detail']}",
            parent=root,
        )
        
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

        output_route = export_excel(vaccinesByPatients, cpms)
        if output_route:
            messagebox.showinfo(
                "Exportación completada",
                f"Se exportaron {len(vaccinesByPatients)} atenciones.\n\n{output_route}"
            )

    #definimos la raiz de la interfaz
    root = tk.Tk()
    root.title("Consultor HIS-MINSA")
    root.geometry("600x350")
    root.protocol("WM_DELETE_WINDOW",     
                  lambda: close(root, lambda:worker_running))
    root.iconbitmap(str(resource_path("assets/icono.ico")))
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)
    
    main_container = tk.Frame(root)
    main_container.grid(
        row=0,
        column=0,
        sticky="nsew")
    
    #Interfaz de la conexión a chrome y el archivo de origen
    getData_container = tk.LabelFrame(main_container, text="Obtener datos")
    getData_container.pack(fill="x", padx=10)

    tk.Label(getData_container, text="Archivo Excel:").pack(anchor='w', padx=10, pady=(20, 4))
    file_entry = tk.Frame(getData_container)
    file_entry.pack(fill="x", padx=10)
    
    input_file = tk.Entry(file_entry)
    input_file.pack(side="left", fill="x", expand=True)

    tk.Button(
        file_entry,
        text="Seleccionar",
        command= lambda: loadExcel(input_file),
    ).pack(side="left", padx=(8, 0))
    
    btn_container = tk.Frame(getData_container)
    btn_container.pack(pady=16, fill="x")
    btn_container.grid_columnconfigure(1,weight=1)
    btn_container.grid_columnconfigure(2,weight=1)
    
    loading_container = tk.Frame(getData_container)
    loading_container.pack(fill="x", padx=10, pady=(0, 8))

    loading_label = tk.Label(loading_container, text="",)
    loading_bar = ttk.Progressbar(loading_container, mode="indeterminate", length=250)

    tk.Button(
        btn_container,
        text="Abrir Chrome para iniciar sesión",
        command=clientHis.openChrome,
    ).grid(column=1, row=0)
    
    btn_connect = tk.Button(
        btn_container,
        text="Conectar y continuar",
        command=connectAndExecute,
    )
    btn_connect.grid(column=2, row=0, )
    
    #interfaz del procesamiento de la informacion
    filters_container = tk.LabelFrame(main_container, text='Procesar Información')
    filters_container.pack(fill='x', padx=10, pady=(8,0), ipady=8)
    
    query_container = tk.Frame(filters_container)
    query_container.pack(fill='x', padx=8, pady=4)
    query_selected = tk.StringVar(value='Ninguna')
    queryID_selected = tk.IntVar(value=0)
        
    tk.Button(query_container, 
              text='seleccionar consulta', 
              command=lambda: queryListWindow(query_container, selectQuery)
              ).grid(column=1, row=0)
    tk.Label(query_container, textvariable=query_selected).grid(column=2, row=0, padx=8)
    
    cpms_container = tk.Frame(filters_container)
    cpms_container.pack(padx=10, anchor='w')
    
    tk.Label(
        cpms_container,
        text="Código CPMS/CIE (mínimo 3 caracteres):",
    ).pack(pady=(16, 4))

    input_codigo = tk.Entry(cpms_container, width=15)
    input_codigo.pack(anchor="w")
    
    tk.Button(filters_container, 
              text="Exportar",
              command=initExport_excel).pack(ipadx=8)

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

        when_select(id_query, file)
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
    query_window.geometry("400x200")
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
    
    for id, date, file, *_ in queries:
        text = f"  ID {id} | {date} | {file}"
        queryList.insert(tk.END, text)
        idsQuery.append(id)
              
    
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
    