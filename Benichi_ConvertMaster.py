import sys
import os
import yt_dlp
import sqlite3
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QLabel, QProgressBar, QFileDialog, QListWidget, QMessageBox, QComboBox, QSplashScreen
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QTimer, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView


# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                email TEXT)''')
    conn.commit()
    conn.close()

# Función para verificar si ya hay usuarios registrados
def check_users_exists():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    result = c.fetchone()
    conn.close()
    return result[0] > 0  # Retorna True si hay usuarios, False si no hay

# Función para registrar un nuevo usuario
def register_user(username, password, email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Encriptar la contraseña antes de almacenarla
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
              (username, hashed_password, email))
    conn.commit()
    conn.close()

# Función para autenticar un usuario
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

class SplashScreenWithText(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.text = "Benichi ConvertMaster"

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))  # Color blanco para el texto
        painter.setFont(QFont("Arial", 15))  # Fuente y tamaño
        text_width = painter.fontMetrics().horizontalAdvance(self.text)
        text_x = (self.pixmap().width() - text_width) // 2  # Centra el texto
        text_y = self.pixmap().height() - 20  # Ajusta la posición vertical
        painter.drawText(text_x, text_y, self.text)
        painter.end()

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

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Benichi ConvertMaster")
        self.setGeometry(400, 200, 400, 400)

        # Estilos generales
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                font-family: Arial;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 5px;
            }
            QLineEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QLabel#error {
                color: #E74C3C;
                font-size: 14px;
            }
        """)

        # Layout principal
        layout = QVBoxLayout()

        # Logo o imagen de bienvenida
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("logo.png").scaled(100, 100, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Título
        self.title_label = QLabel("Bienvenido a Benichi ConvertMaster")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Username
        self.username_label = QLabel("Usuario:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Botón de login
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Mensaje de error
        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if authenticate_user(username, password):
            QMessageBox.information(self, "Login", "¡Inicio de sesión exitoso!")
            self.close()
            self.main_window = BenichiConvertMaster()
            self.main_window.show()
        else:
            self.error_label.setText("Credenciales inválidas, intenta de nuevo.")


class BenichiConvertMaster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Benichi ConvertMaster")
        self.setGeometry(100, 100, 1200, 800)
        
        self.youtube_urls = []

        # Estilos generales
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #ECF0F1;
                font-family: Arial;
            }
            QLabel {
                font-size: 16px;
            }
            QLineEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QComboBox {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                padding: 5px;
            }
            QProgressBar {
                background-color: #34495E;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                text-align: center;
                color: #ECF0F1;
            }
            QListWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
            }
        """)

        # Layout principal
        layout = QVBoxLayout()

        # Título de la aplicación
        self.title_label = QLabel("Benichi ConvertMaster")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Entrada de búsqueda y botón para añadir URL
        search_layout = QVBoxLayout()
        search_container = QWidget()

        self.search_entry = QLineEdit(self, placeholderText="Buscar canción o pegar URL")
        self.search_entry.setStyleSheet("margin-bottom: 10px;")

        add_url_button = QPushButton("Añadir URL", self)
        add_url_button.clicked.connect(self.add_url_to_list)

        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(add_url_button)

        search_container.setLayout(search_layout)
        layout.addWidget(search_container)


        # Ruta de salida
        self.output_path_label = QLabel("Ruta de salida: No seleccionada", self)
        self.output_path_label.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(self.output_path_label)

        browse_button = QPushButton("Seleccionar carpeta de salida", self)
        browse_button.clicked.connect(self.browse_output_path)
        layout.addWidget(browse_button)

        # Selección de formato y resolución
        self.format_selector = QComboBox(self)
        self.format_selector.addItems(["mp3", "mp4"])
        self.format_selector.currentTextChanged.connect(self.toggle_resolution_selector)
        layout.addWidget(self.format_selector)

        self.resolution_selector = QComboBox(self)
        self.resolution_selector.setVisible(False)
        layout.addWidget(self.resolution_selector)

        download_button = QPushButton("Descargar", self)
        download_button.clicked.connect(self.start_download)
        layout.addWidget(download_button)

        # Barra de progreso y estado
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("margin-top: 10px; font-size: 14px;")
        layout.addWidget(self.status_label)

        # Lista de URLs
        self.urls_list = QListWidget(self)
        layout.addWidget(self.urls_list)

        # Navegador web para abrir YouTube
        self.web_view = QWebEngineView(self)
        self.web_view.setUrl(QUrl("https://www.youtube.com"))
        layout.addWidget(self.web_view)
        self.web_view.setMinimumHeight(400)

        # Widget principal y set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def browse_output_path(self):
        output_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if output_path:
            self.output_path_label.setText(f"Ruta de salida: {output_path}")
            self.output_path = output_path

    def add_url_to_list(self):
        url = self.search_entry.text().strip()
        if url.startswith("https://youtu.be/"):
            self.youtube_urls.append(url)
            self.urls_list.addItem(url)
            QMessageBox.information(self, "URL añadida", "El enlace se ha añadido correctamente.")
        else:
            QMessageBox.warning(self, "Error", "Por favor ingrese una URL válida de YouTube que comience con 'https://youtu.be/'.")


    def fetch_resolutions(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                resolutions = sorted(
                    set(f"{f['height']}p" for f in formats if f.get('height') and f['vcodec'] != 'none'),
                    key=lambda x: int(x.replace('p', ''))
                )
                return resolutions
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo obtener la información del video.\n{str(e)}")
            return []

    def toggle_resolution_selector(self):
        selected_format = self.format_selector.currentText()
        self.resolution_selector.setVisible(selected_format == 'mp4')
    
        # Asegúrate de que youtube_urls no esté vacío antes de acceder
        if selected_format == 'mp4' and self.youtube_urls:
            url = self.youtube_urls[-1]
            resolutions = self.fetch_resolutions(url)
            self.resolution_selector.clear()
            if resolutions:
                self.resolution_selector.addItems(resolutions)
            else:
                QMessageBox.warning(self, "Error", "No se encontraron resoluciones disponibles para este video.")
    

    def start_download(self):
        if not self.youtube_urls or not hasattr(self, 'output_path'):
            QMessageBox.warning(self, "Error", "Por favor, selecciona una ruta de salida y añade al menos un enlace.")
            return

        self.progress_bar.setValue(0)
        selected_format = self.format_selector.currentText()
        selected_resolution = self.resolution_selector.currentText() if selected_format == 'mp4' else None

        if selected_format == 'mp4' and not selected_resolution:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una resolución válida para MP4.")
            return

        url = self.youtube_urls[-1]

        self.download_thread = DownloadThread(url, self.output_path, selected_format, selected_resolution)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.download_finished_signal.connect(self.download_complete)
        self.download_thread.start()

    def update_progress(self, percent, message):
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def download_complete(self):
        QMessageBox.information(self, "Descarga completada", "El archivo se descargó correctamente.")
        self.progress_bar.setValue(0)
        self.status_label.clear()
        self.youtube_urls.pop()
        self.urls_list.clear()
        self.search_entry.clear()



if __name__ == '__main__':
    init_db()  # Inicializa la base de datos
    app = QApplication(sys.argv)

    # Crear y mostrar el SplashScreen
    splash_pixmap = QPixmap("logo.png")  # Asegúrate de tener el logo
    splash = SplashScreenWithText(splash_pixmap)
    splash.show()

    # Esperar 2 segundos antes de mostrar el login
    QTimer.singleShot(3000, lambda: splash.close())

    # Mostrar ventana de login después del SplashScreen
    login_window = LoginWindow()
    QTimer.singleShot(3000, lambda: login_window.show())

    sys.exit(app.exec_())

