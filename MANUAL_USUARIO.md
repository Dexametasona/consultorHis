# Manual de usuario
## Consultor HIS-MINSA

**Versión:** 1.0  
**Plataforma:** Windows

## 1. Introducción

Consultor HIS-MINSA es una aplicación de escritorio que permite consultar registros de vacunación de múltiples personas utilizando una lista de DNI almacenada en Excel.

La aplicación automatiza parte del proceso de consulta, guarda los resultados localmente y permite exportarlos para su revisión.

Este manual explica cómo preparar el entorno, ejecutar una consulta y utilizar los resultados de forma segura.

## 2. Requisitos previos

Antes de iniciar, comprueba que dispones de:

- Un equipo con Windows compatible.
- Google Chrome instalado.
- Acceso autorizado a HIS-MINSA.
- Una conexión a Internet activa.
- El paquete de Consultor HIS-MINSA descargado y extraído.

## 3. Instalación

1. Descarga el ZIP desde la sección Releases del repositorio.
2. Extrae el archivo ZIP en una carpeta local.
3. Abre la carpeta extraída.
4. Ejecuta `Consultor HIS-MINSA.exe`.

No ejecutes el programa directamente desde el interior del ZIP. Extrae todos los archivos y conserva la estructura de carpetas original.

Si Windows muestra una advertencia de seguridad, verifica el origen del archivo y las condiciones de distribución antes de continuar.

## 4. Preparar HIS-MINSA

1. Abre Google Chrome.
2. Ingresa a HIS-MINSA.
3. Inicia sesión con tus credenciales autorizadas.
4. Navega al modulo de inmunizaciones y verifica que el campo documento este en DNI.
5. Comprueba que el sistema esté disponible.
6. Mantén abierta la sesión del navegador.

A continuación, utiliza la opción de conexión de Consultor HIS-MINSA para establecer la conexión con Chrome.

Si la aplicación no encuentra una pestaña adecuada, verifica que HIS-MINSA esté abierto y que la sesión sea válida.

**Durante las consultas, no cierres Chrome ni la pestaña de HIS-MINSA.** El programa depende de esa sesión para procesar los DNI. Si el navegador se cierra, la consulta puede interrumpirse.

## 5. Preparar el archivo Excel

El archivo de entrada debe contener los DNI que deseas consultar.

### Recomendaciones

- Coloca los DNI en la primera columna de la hoja activa.
- Utiliza un DNI por fila.
- Evita encabezados u otros valores en la columna de DNI.
- Elimina filas vacías innecesarias.
- Revisa que los DNI sean correctos antes de ejecutar la consulta.
- Guarda una copia del archivo original.

La aplicación está preparada para ignorar filas vacías y normalizar determinados valores numéricos de DNI. No obstante, es recomendable utilizar datos consistentes.

Si un DNI aparece varias veces, utiliza una lista sin duplicados para evitar trabajo innecesario y reducir el riesgo de repetir resultados.

**Ejemplo ilustrativo de estructura:**

| DNI |
|---|
| 12345678 |
| 23456789 |
| 34567890 |

Los números anteriores son ejemplos ficticios y no corresponden a registros de pacientes.

## 6. Ejecutar una consulta

1. Abre Consultor HIS-MINSA.
2. Conecta la aplicación con Chrome y HIS-MINSA.
3. Selecciona el archivo Excel de entrada.
4. Inicia el procesamiento.
5. Observa el indicador de progreso para conocer el avance de las consultas.
6. Espera hasta que la aplicación indique que el procesamiento terminó.

Mientras se ejecuta el proceso:

- No cierres la aplicación.
- No cierres Chrome ni la pestaña de HIS-MINSA.
- Evita modificar manualmente la página que utiliza la aplicación.
- No inicies otra consulta hasta que termine la actual.

Si el navegador se cierra accidentalmente o se pierde la conexión, comprueba el resultado antes de repetir el proceso.

## 7. Consultar el historial

La aplicación almacena información sobre las consultas realizadas en una base de datos SQLite local.

Desde las opciones de historial disponibles en la interfaz, puedes seleccionar una consulta anterior y revisar los resultados asociados.

Antes de eliminar una consulta, comprueba que ya no necesitas sus resultados. Si la operación elimina información asociada, podrías tener que volver a consultar los DNI.

Mantén protegida la base de datos y evita copiarla a equipos o ubicaciones no autorizados.

## 8. Exportar los resultados

Cuando termine una consulta, ingresa el codigo CPMS de la vacuna a filtrar y utiliza la opción de exportación disponible en la interfaz.

El archivo resultante organiza la información de las personas y sus registros de vacunación. Según la estructura de los datos devueltos por HIS-MINSA, puede incluir:

- DNI.
- Nombre del paciente.
- Fecha de nacimiento.
- Códigos CPMS.
- Valores LAB.
- Fechas de los registros.

La organización de las columnas depende de los registros recuperados y de las reglas de exportación de la versión instalada.

### Verificación del archivo

Después de exportar:

1. Abre el archivo en Excel.
2. Comprueba que el número de personas corresponda a la consulta.
3. Revisa que los datos estén asociados al DNI correcto.
4. Verifica que los registros no se hayan duplicado.
5. Comprueba las fechas y los códigos relevantes.
6. Contrasta la información con HIS-MINSA cuando sea necesario.

No utilices un archivo generado por una consulta interrumpida sin verificar previamente que esté completo.

## 9. Solución de problemas

### No se encuentra la pestaña de HIS-MINSA

Abre Chrome, accede a HIS-MINSA e inicia sesión. Luego intenta conectar nuevamente desde la aplicación.

### No se puede conectar con Chrome

Comprueba que Chrome esté abierto y que la configuración de conexión utilizada por la aplicación esté disponible. Cierra y vuelve a abrir la aplicación únicamente cuando no haya una consulta en ejecución.

### El DNI no devuelve registros

Verifica que el DNI sea correcto y que la sesión de HIS-MINSA siga activa. La ausencia de registros devueltos no demuestra por sí sola que una persona nunca haya recibido una vacuna.

### La consulta se interrumpe

Comprueba que Chrome continúe abierto y que HIS-MINSA responda. Revisa los resultados guardados antes de repetir la consulta.

### Excel no muestra los resultados esperados

Comprueba que el archivo exportado sea el correspondiente a la consulta seleccionada y que no existan DNI duplicados en el archivo de entrada.

## 10. Seguridad y confidencialidad

Los datos tratados por la aplicación pueden incluir información personal y sanitaria.

- Consulta únicamente información para la que tengas autorización.
- No envíes archivos reales de pacientes por canales no autorizados.
- No publiques archivos de entrada o salida en repositorios públicos.
- No compartas capturas que muestren nombres, DNI, fechas de nacimiento o historiales.
- Guarda los archivos en ubicaciones institucionales o protegidas.
- Elimina copias temporales cuando ya no sean necesarias, conforme a las políticas aplicables.
- No compartas tus credenciales de acceso a HIS-MINSA.

## 11. Consideraciones finales

Consultor HIS-MINSA es una herramienta de apoyo para automatizar consultas y organizar información. La exactitud y la integridad de los resultados dependen del sistema de origen, de la sesión de consulta y de que el procesamiento termine correctamente.

Ante cualquier discrepancia, verifica la información directamente en HIS-MINSA y sigue los procedimientos de tu institución.
