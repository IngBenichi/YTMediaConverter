# Usamos la imagen base de Python 3.12
FROM python:3.12.6

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos las dependencias del sistema necesarias
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    qt5-qmake \
    qtbase5-dev \
    qtchooser \
    qt5-qmake-bin \
    libqt5webkit5 \
    libxslt-dev \
    libssl-dev \
    libsmime3 \
    libgl1-mesa-glx \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Instalamos las librerías de Python requeridas
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la aplicación dentro del contenedor
COPY . /app/

# Exponemos el puerto si es necesario (esto depende de si tu aplicación usa algún puerto)
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "yt.py"]
