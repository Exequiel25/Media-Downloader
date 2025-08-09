# Media Downloader

Esta aplicación permite buscar y descargar música y videos desde YouTube y Spotify, usando una interfaz gráfica amigable en Tkinter. Puedes buscar por nombre de canción, artista, o directamente por URL de YouTube/Spotify.

## Estructura del Proyecto

```
Media-Downloader
├── MediaDownloader.py         # Script principal para ejecutar la aplicación
├── requirements.txt           # Dependencias necesarias
├── README.md                  # Documentación del proyecto
├── .gitignore                 # Exclusiones de git
├── secret/
│   └── spotify_secrets.txt    # Claves de la API de Spotify (no versionado)
├── src/
│   ├── controller.py          # Lógica de negocio y descargas
│   ├── model.py               # Estructuras de datos y gestión de canciones
│   ├── view.py                # Interfaz gráfica (Tkinter)
│   ├── utils/
│   │   └── search.py          # Funciones utilitarias de búsqueda
│   └── types/
│       └── index.py           # Definiciones de tipos
└── pruebas/                   # Archivos de prueba (no necesarios para ejecución)
```

## Características

- Buscar canciones por nombre, artista o URL (YouTube/Spotify)
- Descargar canciones en formato MP3 o videos en MP4
- Descarga múltiple en paralelo con barra de progreso
- Obtención de metadatos y portadas desde Spotify y YouTube
- Interfaz gráfica intuitiva en español

## Instalación

1. Clona el repositorio:

   ```
   git clone <repository-url>
   cd Media-Downloader
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la aplicación principal:

   ```
   python MediaDownloader.py
   ```

2. Al iniciar, se solicitarán las claves de la API de Spotify si no existen en `secret/spotify_secrets.txt`. Puedes omitirlas, pero no tendrás metadatos avanzados de Spotify.

3. Usa la interfaz para buscar canciones/videos, agregarlos a la lista de descarga y descargarlos en la carpeta que elijas.

## Contribuir

¡Las contribuciones son bienvenidas! Abre un issue o envía un pull request para mejoras o correcciones.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para
