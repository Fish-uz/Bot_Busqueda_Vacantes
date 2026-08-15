# Monitor de vacantes de Telegram

Bot en Python que escucha grupos y canales de Telegram, extrae texto de
publicaciones e imágenes, evita duplicados y utiliza Groq con Gemini como
respaldo para decidir qué vacantes reenviar a Mensajes guardados.

También puede consultar periódicamente Computrabajo, Bumeran y Gente Top. Esta
función es optativa porque algunos portales pueden exigir JavaScript o cambiar
su HTML sin aviso.

## Requisitos

- Python 3.10 o superior.
- Credenciales de API de Telegram.
- Una clave de Groq o Gemini (se recomienda configurar ambas).
- Tesseract OCR. En Windows se busca por defecto en
  `C:\Program Files\Tesseract-OCR\tesseract.exe`.

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuración

Cree `.env` en la raíz:

```dotenv
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=tu_api_hash
TELEGRAM_GRUPOS_VACANTES=-1001234567890,-1009876543210
GROQ_API_KEY=tu_clave_groq
GEMINI_API_KEY=tu_clave_gemini
```

Opciones adicionales:

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
SCRAPING_ENABLED=false
SCRAPING_INTERVAL_MINUTES=60
```

Las rutas relativas se interpretan desde el directorio desde el que se inicia el
proceso; los valores predeterminados apuntan a la raíz del proyecto.

Para listar grupos accesibles:

```powershell
python client_telegram.py
```

La sesión de Telegram (`*.session`) equivale a una credencial. No debe
publicarse, copiarse a logs ni enviarse a terceros.

## Ejecución

```powershell
python main.py
```

Al arrancar, el programa valida credenciales, IDs de grupos y disponibilidad de
al menos un proveedor de IA. Si la conexión con Telegram falla, el proceso se
detiene con un error visible en lugar de quedar escuchando sin conexión.

El flujo por mensaje es:

1. Combinar el pie de foto y el resultado OCR cuando exista una imagen.
2. Reservar atómicamente su hash en SQLite.
3. Analizar fuera del bucle asíncrono con Groq y, si falla, Gemini.
4. Marcarlo como procesado o como error reintentable.
5. Reenviar las coincidencias al destino configurado.

`log_ocr.txt` registra únicamente fecha, grupo, decisión y hash; no guarda el
texto completo del anuncio. El log técnico rota en archivos de 5 MB.

## Portales de empleo

Para activar `scrapings/` junto al monitor:

```dotenv
SCRAPING_ENABLED=true
SCRAPING_INTERVAL_MINUTES=60
```

El intervalo mínimo aceptado es 15 minutos. El primer ciclo comienza al arrancar
el bot y los siguientes se ejecutan con el intervalo configurado. Los tres
portales comparten la misma base de deduplicación, el fallback de IA y el destino
de Telegram.

Cada fuente tiene un parser independiente:

- `scraper_computrabajo.py`
- `scraper_bumeran.py`
- `scraper_gentetop.py`

La descarga utiliza solamente páginas públicas y no intenta resolver CAPTCHA,
evadir controles anti-bot ni iniciar sesión. Si un portal requiere JavaScript o
bloquea la solicitud, el error se registra y las demás fuentes continúan.

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas no llaman a Telegram ni a proveedores de IA y utilizan bases SQLite
temporales.

## Archivos locales protegidos

`.gitignore` excluye `.env`, sesiones de Telegram, bases SQLite, logs e imágenes
temporales. `Log_ocr.txt` fue retirado del índice de Git durante el saneamiento;
su copia local no se elimina automáticamente.

Si una sesión o clave fue publicada alguna vez, debe revocarse. Añadir el archivo
a `.gitignore` no lo borra del historial previo de Git.

## Limitaciones pendientes

- Los selectores de portales pueden necesitar mantenimiento cuando cambie su HTML.
- Computrabajo puede solicitar validación JavaScript y no ofrecer HTML utilizable
  a clientes HTTP automatizados.
- En la comprobación del 15 de agosto de 2026, Computrabajo y Bumeran respondieron
  HTTP 403 y Gente Top devolvió un intersticial JavaScript hacia `/lander`. El bot
  detecta estos casos, los registra y continúa; no intenta eludir el bloqueo.
- Álbumes, PDF y documentos que no sean fotos aún no se procesan.
- La clasificación por IA puede producir falsos positivos o negativos y debe
  revisarse periódicamente.
- No existe todavía CI ni configuración automática de linting/cobertura.
