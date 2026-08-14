# Monitor de vacantes de Telegram con IA y OCR

Bot en Python que escucha grupos y canales de Telegram, extrae el texto de las
publicaciones (incluidas imágenes mediante OCR), descarta duplicados y utiliza
modelos de IA para decidir si una vacante coincide con los perfiles y ubicaciones
configurados. Las coincidencias se reenvían a **Mensajes guardados** de Telegram.

> Estado: el monitor de Telegram es el flujo principal del proyecto. Los scrapers
> de portales de empleo incluidos en `scrapings/` son prototipos independientes y
> actualmente necesitan ajustes antes de poder ejecutarse (véase
> [Limitaciones conocidas](#limitaciones-conocidas)).

## Funcionalidades

- Escucha en tiempo real de varios grupos o canales con Telethon.
- Procesamiento de publicaciones de texto e imágenes.
- OCR local con Tesseract y Pillow.
- Clasificación principal con Groq (`llama-3.1-8b-instant`).
- Respaldo automático con Gemini (`gemini-1.5-flash`) si Groq falla.
- Filtro anti-duplicados mediante hashes almacenados en SQLite.
- Limpieza mensual automática del historial de hashes.
- Reenvío de coincidencias a Mensajes guardados.
- Registro técnico en consola, `bot_vigilancia.log` y `log_ocr.txt`.

## Cómo funciona

```text
Mensaje nuevo de Telegram
          |
          +-- texto -----------+
          |                     |
          +-- imagen -> OCR ----+
                                |
                       validar contenido
                                |
                       comprobar duplicado
                                |
                    Groq -> fallback Gemini
                                |
                 relevante? -- sí --> reenviar
                                |
                               no --> descartar
```

La relevancia se define actualmente en `cerebro.py`. El prompt acepta puestos de
tecnología, automatización, administración, banca, contabilidad y finanzas para
Caracas, Miranda, Distrito Capital o trabajo 100 % remoto, y excluye varias áreas
no deseadas.

## Requisitos

- Python 3.10 o superior (recomendado).
- Una cuenta de Telegram y credenciales de API obtenidas en
  [my.telegram.org](https://my.telegram.org/).
- Una clave de API de Groq.
- Una clave de API de Google Gemini para el respaldo.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado:
  - Windows: la aplicación espera por defecto
    `C:\Program Files\Tesseract-OCR\tesseract.exe`.
  - Linux: la aplicación espera `/usr/bin/tesseract`.

## Instalación

En PowerShell:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd Bot_Vacantes
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Linux o macOS, active el entorno con `source venv/bin/activate`.

## Configuración

Cree un archivo `.env` en la raíz del proyecto:

```dotenv
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=tu_api_hash
TELEGRAM_GRUPOS_VACANTES=-1001234567890,-1009876543210
GROQ_API_KEY=tu_clave_groq
GEMINI_API_KEY=tu_clave_gemini
```

`TELEGRAM_GRUPOS_VACANTES` admite varios IDs separados por comas. Los IDs de
supergrupos y canales suelen comenzar por `-100`.

Las variables `TELEGRAM_MI_GRUPO` y `TELEGRAM_OWNER_ID` pueden existir en una
configuración local antigua, pero el código actual no las utiliza.

Nunca publique `.env`, archivos `*.session`, claves, tokens ni copias de la base
de datos. La sesión de Telethon permite acceder a la cuenta asociada y debe
tratarse como una contraseña.

### Obtener IDs de grupos y canales

Con la configuración de Telegram lista, ejecute:

```powershell
python client_telegram.py
```

En el primer inicio, Telegram solicitará por consola el número telefónico, el
código de acceso y, si está habilitada, la contraseña de verificación en dos
pasos. El script mostrará los nombres e IDs disponibles y creará localmente
`sesion_frank.session`.

## Ejecución

```powershell
python main.py
```

El proceso permanece escuchando hasta presionar `Ctrl+C`. Cuando detecta una
vacante relevante, reenvía la publicación original a Mensajes guardados.

Durante la ejecución se crean estos archivos locales:

- `vacantes_data.db`: hashes usados por el filtro anti-spam.
- `bot_vigilancia.log`: eventos técnicos del proceso.
- `log_ocr.txt`: contenido procesado para auditoría; se reinicia al superar
  100 MB.
- `temp_images/`: imágenes descargadas temporalmente y eliminadas tras el OCR.
- `sesion_frank.session`: sesión autenticada de Telegram.

## Pruebas

```powershell
pytest -q
```

La suite actual no es completamente aislada: `test_cerebro.py` realiza llamadas
reales a proveedores de IA y requiere claves y conexión. Para una suite estable,
esas respuestas deberían simularse y las pruebas de base de datos deberían usar
un archivo temporal.

## Estructura del proyecto

```text
.
|-- main.py                 # Punto de entrada
|-- client_telegram.py      # Cliente, autenticación y listado de chats
|-- monitor.py              # Recepción y procesamiento de mensajes
|-- cerebro.py              # Prompt y clasificación Groq/Gemini
|-- ocr_engine.py           # Extracción de texto con Tesseract
|-- database.py             # Persistencia anti-duplicados en SQLite
|-- config.py               # Variables de entorno y logging
|-- utils.py                # Hashing y salida coloreada
|-- scrapings/              # Prototipos de scrapers independientes
|-- test/                   # Pruebas automatizadas
|-- Screenshots/            # Capturas de ejemplo
`-- requirements.txt        # Dependencias Python
```

## Limitaciones conocidas

- Los scrapers importan `es_mensaje_repetido`, función que ya no existe en
  `utils.py`, y `beautifulsoup4` no está declarado en `requirements.txt`. Tampoco
  se programan ni se invocan desde `main.py`.
- `google-generativeai` está oficialmente obsoleto y emite una advertencia al
  importar; el fallback debe migrarse al paquete mantenido `google-genai`.
- `test_utils.py` aún prueba el antiguo sistema basado en archivo
  (`HASH_FILE`/`es_mensaje_repetido`), mientras la aplicación ya usa SQLite; por
  eso la colección de pruebas falla actualmente.
- El mock exitoso de `test_mock_ejemplo.py` devuelve `TRUE - ...`, pero el parser
  exige `DECISION: TRUE`; esa prueba no refleja el contrato vigente.
- Las llamadas síncronas a Groq, Gemini, Tesseract y `requests` se ejecutan dentro
  de funciones asíncronas. Bajo mucho tráfico pueden bloquear temporalmente la
  recepción de nuevos mensajes.
- El hash se guarda antes del análisis. Si ambos proveedores fallan, la publicación
  queda marcada como procesada y no se reintentará durante ese mes.
- Las rutas de Tesseract están fijas en el código y no se pueden configurar desde
  `.env`.
- Los mensajes con álbumes, documentos que no sean fotos y publicaciones editadas
  no tienen tratamiento específico.
- `log_ocr.txt` puede contener datos personales presentes en las vacantes. Debe
  protegerse y aplicársele una política de retención apropiada.
- `Log_ocr.txt` ya está versionado en Git pese a la regla de exclusión. Además,
  `vacantes_data.db` no figura en `.gitignore`; ambos pueden terminar publicando
  datos operativos o personales.

## Mejoras recomendadas

Prioridad alta:

1. Reparar y aislar la suite de pruebas, evitando llamadas reales a APIs.
2. Retirar del índice de Git los logs/datos locales y excluir `*.db` sin borrar la
   copia de trabajo necesaria para ejecutar el bot.
3. Validar al inicio las variables requeridas y detenerse con un mensaje claro si
   falta alguna o si no hay grupos configurados.
4. Guardar el hash solo después de un análisis exitoso, o registrar estados
   `pendiente`, `procesado` y `error` para permitir reintentos.
5. Ejecutar OCR y clientes síncronos fuera del event loop (`asyncio.to_thread`) o
   migrar a clientes asíncronos.
6. Migrar de `google-generativeai` a `google-genai`.
7. Incorporar rotación real para ambos logs y evitar almacenar texto sensible si
   no es imprescindible.

Prioridad media:

1. Hacer configurables el modelo, perfiles, ubicaciones, ruta/idioma de Tesseract,
   destino de Telegram y tiempos de espera.
2. Añadir reintentos con espera exponencial y distinguir errores temporales de
   respuestas negativas del modelo.
3. Usar salida estructurada o JSON para validar de forma robusta la decisión de IA.
4. Decidir si los scrapers serán parte del producto: integrarlos con un scheduler
   y SQLite, o retirarlos para reducir mantenimiento.
5. Agregar cierre ordenado del cliente de Telegram, tipado, linting y CI.

## Seguridad y uso responsable

- Use únicamente grupos y fuentes a los que tenga acceso legítimo y respete sus
  condiciones de uso.
- No registre ni comparta credenciales o sesiones.
- Revise manualmente las coincidencias: la clasificación por IA puede producir
  falsos positivos y falsos negativos.
- Si una credencial o archivo de sesión llegó a publicarse, revoque o rote el
  acceso; añadirlo después a `.gitignore` no lo elimina del historial de Git.

## Licencia

El repositorio no incluye actualmente un archivo de licencia. Añada uno antes de
distribuir o aceptar contribuciones externas.
