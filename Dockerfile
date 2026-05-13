# 1. Imagen base de Python ligera
FROM python:3.11-slim

# 2. Instalación de dependencias del sistema (Tesseract OCR)
RUN apt-get update && apt-get install -y \
 tesseract-ocr \
 libtesseract-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo en el contenedor
WORKDIR /app

# 4. Instalación de dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código fuente
COPY . .

# 6. Comando de arranque
CMD ["python", "main.py"]