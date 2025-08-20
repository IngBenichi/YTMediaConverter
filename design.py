from PyQt5.QtWidgets import ( QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QLabel, QProgressBar, QFileDialog, QListWidget, QMessageBox, QComboBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from download import DownloadThread

class SonicMingle(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Benichi ConvertMaster")
        self.setGeometry(100, 100, 1200, 800)

        self.youtube_urls = []
        self.download_thread = None

        # Layout principal
        layout = QVBoxLayout()

        # Widgets de entrada y botones
        self.search_entry = QLineEdit(self, placeholderText="Buscar canción o pegar URL")
        self.search_entry.returnPressed.connect(self.search_videos)
        layout.addWidget(self.search_entry)

        self.output_path_label = QLabel("Ruta de salida: No seleccionada", self)
        layout.addWidget(self.output_path_label)

        browse_button = QPushButton("Seleccionar carpeta de salida", self)
        browse_button.clicked.connect(self.browse_output_path)
        layout.addWidget(browse_button)

        self.format_selector = QComboBox(self)
        self.format_selector.addItems(["mp3", "mp4"])
        self.format_selector.currentTextChanged.connect(self.toggle_resolution_selector)
        layout.addWidget(self.format_selector)

        self.resolution_selector = QComboBox(self)
        self.resolution_selector.addItems(["144p", "360p", "720p", "1080p"])
        self.resolution_selector.setVisible(False)  # Ocultar inicialmente
        layout.addWidget(self.resolution_selector)

        download_button = QPushButton("Descargar", self)
        download_button.clicked.connect(self.start_download)
        layout.addWidget(download_button)

        # Barra de progreso y estado
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        # Lista de URLs
        self.urls_list = QListWidget(self)
        layout.addWidget(self.urls_list)

        # Navegador web para abrir YouTube
        self.web_view = QWebEngineView(self)
        self.web_view.setUrl(QUrl("https://www.youtube.com"))
        layout.addWidget(self.web_view)
        self.web_view.setMinimumHeight(600)

        # Widget principal y set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def browse_output_path(self):
        output_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if output_path:
            self.output_path_label.setText(f"Ruta de salida: {output_path}")
            self.output_path = output_path

    def search_videos(self):
        url = self.search_entry.text().strip()
        if url.startswith("https://youtu.be/"):
            self.youtube_urls.append(url)
            self.urls_list.addItem(url)
            QMessageBox.information(self, "URL añadida", "El enlace se ha añadido correctamente.")
        else:
            QMessageBox.warning(self, "Error", "Por favor ingrese una URL válida de YouTube que comience con 'https://youtu.be/'.")

    def start_download(self):
        if not self.youtube_urls or not self.output_path:
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
        self.download_thread.download_finished_signal.connect(self.download_finished)  # Conectar la señal de finalización
        self.download_thread.start()

    def toggle_resolution_selector(self):
        selected_format = self.format_selector.currentText()
        self.resolution_selector.setVisible(selected_format == 'mp4')

    def update_progress(self, percent, status):
        self.progress_bar.setValue(percent)
        self.status_label.setText(status)

    def download_finished(self):
        QMessageBox.information(self, "Descarga finalizada", "La descarga se ha completado con éxito.")
        self.reset_fields()

    def reset_fields(self):
        # Restablece todos los campos y la interfaz
        self.youtube_urls.clear()
        self.urls_list.clear()
        self.search_entry.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("")
