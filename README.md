# Bot de vacantes de Telegram

Aplicación en Python que monitorea grupos y canales de Telegram, analiza sus
publicaciones y reenvía a Mensajes guardados las vacantes compatibles con los
perfiles configurados en el proyecto.

El bot admite publicaciones de texto e imágenes. Cuando recibe una imagen,
utiliza Tesseract OCR para extraer su contenido antes de enviarlo al filtro de
inteligencia artificial.

## Cómo funciona

Por cada publicación nueva, el bot realiza este proceso:

1. Obtiene el texto del mensaje.
2. Si contiene una imagen, extrae su texto mediante OCR y lo combina con el pie
   de foto.
3. Genera una huella SHA-256 para evitar procesar publicaciones duplicadas.
4. Envía el contenido a Groq para determinar si corresponde a los perfiles y
   ubicaciones buscados.
5. Si Groq no está disponible, utiliza Gemini como respaldo.
6. Si la vacante es relevante, reenvía la publicación original al destino de
   Telegram configurado.

Los hashes y sus estados se almacenan en SQLite. Cuando ocurre un error de IA,
la publicación queda disponible para un intento posterior en lugar de marcarse
como rechazada.

## Requisitos

- Python 3.10 o superior.
- Una cuenta de Telegram.
- Credenciales de API de Telegram obtenidas en
  [my.telegram.org](https://my.telegram.org/).
- Una clave de Groq o Gemini. Se recomienda configurar ambas.
- Tesseract OCR para procesar imágenes.

En Windows, la ruta predeterminada de Tesseract es:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Instalación

Abra PowerShell en la carpeta del proyecto y cree un entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuración

Cree un archivo `.env` en la raíz del proyecto:

```dotenv
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=tu_api_hash
TELEGRAM_GRUPOS_VACANTES=-1001234567890,-1009876543210

GROQ_API_KEY=tu_clave_groq
GEMINI_API_KEY=tu_clave_gemini
```

`TELEGRAM_GRUPOS_VACANTES` acepta varios IDs separados por comas. Para consultar
los grupos y canales disponibles en la cuenta, ejecute:

```powershell
python client_telegram.py
```

En la primera ejecución, Telegram solicitará el número telefónico, el código de
autenticación y, si corresponde, la contraseña de verificación en dos pasos.

### Kuentro

Kuentro se integra mediante su canal oficial de Telegram, `@kuentroapp`:

1. Únase a `@kuentroapp` con la cuenta utilizada por el bot.
2. Ejecute `python client_telegram.py`.
3. Copie el ID numérico de `Kuentro | Trabajo - Empleos`.
4. Añada el ID a `TELEGRAM_GRUPOS_VACANTES`.

Las publicaciones de Kuentro serán procesadas igual que las de cualquier otro
grupo o canal configurado.

## Opciones adicionales

Estas variables son opcionales:

```dotenv
TELEGRAM_DESTINO=me
TELEGRAM_SESSION=sesion_frank

GROQ_MODEL=llama-3.1-8b-instant
GEMINI_MODEL=gemini-3.5-flash

TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_LANG=spa

VACANTES_DB_PATH=vacantes_data.db
OCR_LOG_PATH=log_ocr.txt
TEMP_IMAGES_DIR=temp_images
```

`TELEGRAM_DESTINO=me` envía las coincidencias a Mensajes guardados.

## Ejecución

Con el entorno virtual activado:

```powershell
python main.py
```

El proceso permanecerá escuchando hasta que se cierre con `Ctrl+C`.

Al iniciar, el programa valida:

- Las credenciales de Telegram.
- Los IDs de grupos y canales.
- La presencia de al menos una clave de IA.
- La conexión y autorización de la sesión de Telegram.

## Pruebas

Para ejecutar la suite automatizada:

```powershell
python -m pytest -q
```

Las pruebas utilizan respuestas simuladas y bases SQLite temporales. No envían
mensajes ni consumen las APIs de Groq, Gemini o Telegram.

## Archivos generados

Durante la ejecución pueden crearse:

- `sesion_frank.session`: sesión autenticada de Telegram.
- `vacantes_data.db`: base SQLite del sistema anti-duplicados.
- `bot_vigilancia.log`: registro técnico rotativo.
- `log_ocr.txt`: fecha, grupo, resultado y hash de publicaciones procesadas.
- `temp_images/`: imágenes temporales eliminadas después del OCR.

Estos archivos, junto con `.env`, están excluidos de Git. La sesión de Telegram
y las claves de API deben tratarse como credenciales privadas.

## Estructura principal

```text
main.py                 Inicio de la aplicación
client_telegram.py      Conexión, autenticación y listado de canales
monitor.py              Recepción y procesamiento de publicaciones
cerebro.py              Clasificación con Groq y Gemini
ocr_engine.py           Extracción de texto con Tesseract
database.py             Deduplicación y estados en SQLite
config.py               Variables de entorno, rutas y logging
utils.py                Normalización y generación de hashes
test/                    Pruebas automatizadas
```
