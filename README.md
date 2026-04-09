# 📚 RescateTMO (Híbrido: Web + Multihistorial)

**RescateTMO** es una herramienta avanzada en Python diseñada para consolidar tu progreso de lectura de manga. Esta versión sincroniza tus listas de **Nakamasweb** con tus historiales locales de **Chrome, Edge, Opera y Firefox**, generando un reporte unificado y ordenado.

---

## 🛠️ Requisitos Previos

### 1. Instalar Python
Descárgalo en [python.org](https://www.python.org/). 
> **IMPORTANTE:** Durante la instalación, marca la casilla **"Add Python to PATH"**.

### 2. Navegador Google Chrome
El script utiliza **Selenium** para la parte web, por lo que requiere tener Chrome instalado.

### 3. Instalación de Librerías
Abre una terminal en la carpeta del proyecto y ejecuta:
```
python -m pip install selenium webdriver-manager python-dotenv
```
🚀 Configuración y Uso

1. Configurar Credenciales (.env)

Busca el archivo .env.example en el proyecto.

Cópialo y renómbralo a .env.

Rellena tus datos:
```markdown

USER_EMAIL=tu_correo@ejemplo.com
USER_PASS=tu_contraseña_aqui
```

2. Sincronización de Historial Local (Opcional)

Chrome: copia el archivo History desde: %LOCALAPPDATA%/Google/Chrome/User Data/Default/ y pégalo junto al script.

Firefox: copia places.sqlite desde tu carpeta de perfil.

3. Ejecución del Script

Ejecuta:
```
python RescateTMO.py
```
Si aparece un CAPTCHA, resuélvelo y pulsa “Acceder”. El script detectará el inicio de sesión y comenzará la extracción.

📄 Formato del Reporte de Salida

El script generará un archivo llamado MIS_MANGAS_RESCATADOS.txt con este formato:
FUENTE DE ORIGEN	ESTADO	CAP	NOMBRE DEL MANGA
Web	Pendientes	0.0	Nombre del Manga A
Historial_Chrome	Siguiendo	15.2	Nombre del Manga B
Historial_Firefox	Siguiendo	8.0	Nombre del Manga C
Lógica de Clasificación:

    Siguiendo: Cualquier manga con un capítulo superior a 0.0 detectado en el historial.

    Pendientes: Mangas que están en tu lista pero no tienen registro de lectura (Cap 0.0).

    Prioridad de Origen: Si un manga aparece en varias fuentes, se mostrará la fuente que tenga el capítulo más alto.

⚠️ Privacidad y Seguridad

El archivo .env contiene tu contraseña. Nunca lo compartas.

.gitignore está configurado para ignorar credenciales e historiales.

Todo el proceso ocurre localmente. No se envía información a terceros.

⚖️ Licencia

Este proyecto está bajo la Licencia MIT.
