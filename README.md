# Benichi ConvertMaster

Este proyecto utiliza `PyQt5` y `yt_dlp` para crear una aplicación gráfica que descarga y convierte videos de YouTube.

## Requisitos Previos

1. **Python 3.12.6 o superior** (asegúrate de que esté instalado).
2. **`ffmpeg`**: Descárgalo y colócalo en la carpeta `bin` junto al proyecto, o asegúrate de que esté accesible desde el sistema.

## Configuración del Entorno Virtual

1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   ```

2. Activa el entorno virtual:
   - En Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - En macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Instala las dependencias desde el archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

1. **Interfaz gráfica (GUI):**
   - Permite buscar videos o pegar URLs de YouTube.
   - Seleccionar la carpeta de salida para guardar los archivos descargados.
   - Elegir el formato de descarga (MP3 o MP4).
   - Seleccionar la resolución del video si se descarga en MP4 (opciones como 144p, 360p, 720p, etc.).

2. **Descarga y conversión:**
   - Utiliza `yt_dlp` para gestionar la descarga de videos.
   - Si se selecciona MP3, realiza un post-procesamiento con `ffmpeg` para extraer el audio.
   - Muestra el progreso de la descarga en tiempo real con una barra de progreso.

3. **Manejo de múltiples URLs:**
   - Permite agregar URLs a una lista de descarga.
   - Valida que las URLs pertenezcan a YouTube.

4. **Navegación web:**
   - Incorpora un navegador embebido basado en `QWebEngineView` para explorar YouTube directamente desde la aplicación.

5. **Multitarea con hilos:**
   - Usa `QThread` para realizar las descargas en segundo plano, evitando que la interfaz se congele.

6. **Notificaciones:**
   - Muestra mensajes emergentes (con `QMessageBox`) para informar sobre errores, el estado de la descarga o su finalización.

En resumen, es un gestor de descargas sencillo y visual para YouTube, con soporte para audio y video en diferentes formatos y calidades.
