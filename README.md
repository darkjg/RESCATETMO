📚 RescateTMO

RescateTMO es una herramienta automatizada en Python diseñada para recuperar tu progreso de lectura de manga, manhwa y manhua directamente desde el historial local de tus navegadores (Firefox o Google Chrome).

Si has perdido tu cuenta o simplemente quieres una lista organizada de lo último que has leído en ZonaTMO, este script escanea tu historial, elimina duplicados, extrae el número del último capítulo y genera un reporte limpio en un archivo de texto.

🛠️ Requisitos Previos (Instalación)

Para poder usar este script, necesitas tener instalado Python en tu ordenador.

1. Instalar Python

Si no lo tienes instalado:

Ve a la página oficial: python.org.

Descarga e instala la última versión para tu sistema operativo.

IMPORTANTE (Windows): Durante la instalación, marca la casilla que dice "Add Python to PATH". Esto permite ejecutar el script desde cualquier terminal.

### 2. Instalación de Librerías
Este script utiliza librerías nativas de Python, por lo que no requiere instalaciones complejas. Puedes verificar que todo está listo ejecutando estos comandos en tu terminal:

```bash
# Comprobar versión de Python
# Actualizar el gestor de paquetes
python -m pip install --upgrade pip

# Instalar librerías necesarias (si decides ampliar el script)
pip install pandas openpyxl
```
🚀 Cómo usar el Script

1. Obtener los archivos de historial

Debes copiar el archivo de historial de tu navegador a la carpeta donde se encuentra RescateTMO.py:

Firefox: 1. Abre Firefox y escribe about:support en la barra de direcciones.
2. Busca Ruta del perfil y haz clic en "Abrir carpeta".
3. Copia el archivo places.sqlite a la carpeta del script.

Google Chrome: 1. Presiona Win + R, escribe %LOCALAPPDATA%\Google\Chrome\User Data\Default\ y pulsa Enter.
2. Busca el archivo llamado History (sin extensión) y cópialo a la carpeta del script.

2. Ejecución

Abre una terminal en la carpeta donde están los archivos y escribe:

python RescateTMO.py


📄 Resultado

El script generará automáticamente un archivo llamado LISTA_TMO.txt con el siguiente formato:

[001.00] - Berserk
[165.50] - Chainsaw Man
[000.00] - Solo Leveling 


⚠️ Privacidad (IMPORTANTE)

Este proyecto es de uso personal y local. Nunca subas tus archivos places.sqlite o History a GitHub ni a ningún sitio público, ya que contienen información privada de toda tu navegación web.

Este repositorio incluye un archivo .gitignore para evitar que tus datos personales se suban a la nube por accidente.

⚖️ Licencia

Este proyecto está bajo la Licencia MIT.
