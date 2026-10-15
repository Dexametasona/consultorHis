# Consultor HIS-MINSA

Aplicación de escritorio para Windows que automatiza la consulta de historiales de atenciones y vacunación en HIS-MINSA a partir de una lista de DNI en Excel.

## Descripción

Consultor HIS-MINSA permite consultar múltiples personas de forma consecutiva, organizar los resultados y exportarlos a Excel para facilitar su revisión y análisis.

La aplicación utiliza Playwright para interactuar con una sesión existente de Chrome, SQLite para almacenar las consultas y sus resultados, y OpenPyXL para procesar archivos Excel.

El objetivo es reducir el trabajo manual que implica consultar individualmente numerosos DNI en HIS-MINSA.

## Características

- **Consulta por lotes:** importa una lista de DNI desde Excel y procesa las consultas de manera consecutiva.
- **Integración con HIS-MINSA:** utiliza una sesión de Chrome conectada mediante Playwright y CDP.
- **Consulta de vacunaciones:** recopila códigos CPMS, valores LAB y fechas de los registros devueltos por HIS-MINSA.
- **Exportación a Excel:** organiza la información obtenida para facilitar su revisión.
- **Historial de consultas:** guarda las consultas realizadas en una base de datos SQLite.
- **Persistencia local:** permite conservar y consultar resultados de ejecuciones anteriores.
- **Interfaz gráfica:** permite ejecutar las operaciones principales desde una aplicación de escritorio.
- **Procesamiento por lotes:** muestra el avance de las consultas mientras se procesan los DNI.

## Requisitos

Para utilizar la versión distribuida se necesita:

- Un equipo con Windows compatible con la versión publicada.
- Google Chrome instalado.
- Acceso autorizado a HIS-MINSA.
- Conexión a Internet.
- El paquete de distribución descargado desde GitHub Releases.

La versión distribuida incluye el ejecutable y las dependencias empaquetadas por PyInstaller. No debería ser necesario instalar Python por separado.

## Instalación

1. Ingresa a la sección **Releases** del repositorio.
2. Descarga el archivo ZIP de la versión que deseas utilizar.
3. Extrae su contenido en una carpeta local.
4. Ejecuta `Consultor HIS-MINSA.exe`.
5. Abre HIS-MINSA en Chrome e inicia sesión con tus credenciales autorizadas.
6. Utiliza la opción de conexión de la aplicación para conectarla con la sesión del navegador.

**Importante:** conserva la estructura de archivos y carpetas incluida en el paquete extraído. No muevas el ejecutable fuera de su carpeta de distribución.

## Uso general

El flujo de trabajo es el siguiente:

1. Abrir la aplicación y preparar la sesión de HIS-MINSA en Chrome.
2. Conectar la aplicación con el navegador.
3. Seleccionar el archivo Excel que contiene los DNI.
4. Ejecutar la consulta.
5. Esperar a que finalice el procesamiento.
6. Revisar los resultados y utilizar las opciones disponibles para consultar el historial o exportar la información a Excel.

Para obtener instrucciones detalladas, consulta el archivo [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md).

## Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **Tkinter y ttk:** interfaz gráfica.
- **Playwright:** automatización del navegador.
- **SQLite:** almacenamiento local.
- **OpenPyXL:** lectura y escritura de archivos Excel.
- **PyInstaller:** empaquetado para Windows.

## Estructura del proyecto

La organización modular separa la interfaz gráfica, la lógica de consulta, el acceso a la base de datos y las utilidades.

```text
Consultor-HIS-MINSA/
├── assets/
├── database/
├── services/
├── ui/
├── utils/
├── main.py
└── README.md
```

La estructura puede variar según la versión publicada.

## Privacidad y seguridad

Los archivos Excel, los historiales consultados y la base de datos pueden contener información personal y sanitaria sensible.

- Utiliza la aplicación únicamente para fines autorizados.
- No publiques archivos reales de pacientes en GitHub.
- No compartas capturas, registros de depuración ni archivos que expongan DNI, nombres, fechas de nacimiento o historiales clínicos.
- No compartas credenciales, cookies ni tokens de sesión.
- Protege la carpeta donde se almacenan los resultados y la base de datos.
- Verifica que los resultados exportados correspondan a las personas consultadas antes de utilizarlos.

El almacenamiento local no sustituye las medidas de seguridad, confidencialidad y control de acceso que correspondan a la institución.

## Limitaciones

- La consulta depende de la disponibilidad y del funcionamiento de HIS-MINSA.
- Los resultados dependen de la información que el sistema de origen devuelve.
- Los cambios en la interfaz o en las peticiones de HIS-MINSA pueden requerir actualizaciones de la aplicación.
- La aplicación no sustituye la verificación de los registros en el sistema oficial.

## Solución de problemas

**La aplicación no encuentra HIS-MINSA**

Abre Chrome desde la aplicación, ingresa a HIS-MINSA, inicia sesión, navega al modulo de Inmunizaciones y verifica que en Documento este seleccionado DNI. Comprueba que el navegador esté disponible para la conexión de la aplicación.

**La consulta falla o devuelve un error**

Verifica la conexión a Internet, el acceso a HIS-MINSA y que la sesión continúe activa. Si el problema persiste, registra el mensaje de error sin incluir datos personales.

**El archivo Excel no se procesa**

Comprueba que el archivo sea compatible con Excel y que los DNI estén en la primera columna. Revisa que no existan filas con formatos inesperados.

**La aplicación se cierra inesperadamente**

Vuelve a abrirla y revisa si se generó algún mensaje de error. No asumas que una consulta interrumpida se completó correctamente.

## Licencia

La licencia y las condiciones de distribución deben consultarse en los archivos publicados en este repositorio.

## Autor

Alexander Machicado G.
