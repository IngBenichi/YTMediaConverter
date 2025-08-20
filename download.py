import os
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp
class DownloadThread(QThread):
    progress_signal = pyqtSignal(int, str)
    download_finished_signal = pyqtSignal()  # Señal para indicar que la descarga ha finalizado

    def __init__(self, url, output_path, format, resolution):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format = format
        self.resolution = resolution

    def run(self):
        try:
            # Selección del formato de descarga
            format_selection = (
                f'bestvideo[height<={self.resolution}]+bestaudio/best' 
                if self.format == 'mp4' else 'bestaudio/best'
            )
            
            # Configuración de las opciones de yt-dlp
            ydl_opts = {
                'format': format_selection,
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'ffmpeg_location': os.path.join(os.path.dirname(__file__), 'bin', 'ffmpeg.exe'),
                'progress_hooks': [self.progress_hook],
            }

            # Agregar el post-procesamiento si el formato es MP3
            if self.format == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            # Emite la señal de finalización de la descarga después de que haya terminado
            self.download_finished_signal.emit()

        except Exception as e:
            print(f"Error en descarga: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Calcular el porcentaje como número entero
            percent = int(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100)

            # Obtener el tiempo restante en segundos y convertir a minutos y segundos
            remaining_time_seconds = d.get('eta', 0) or 0
            minutes, seconds = divmod(int(remaining_time_seconds), 60)
            formatted_time = f"{minutes}m {seconds}s"

            # Emitir la señal de progreso con el porcentaje y el tiempo formateado
            self.progress_signal.emit(percent, f"Descargando... {percent}% - Tiempo restante: {formatted_time}")
        elif d['status'] == 'finished':
            # Emitir señal indicando que la descarga ha finalizado
            self.progress_signal.emit(100, "Descarga finalizada")
