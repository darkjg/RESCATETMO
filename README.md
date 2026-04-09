📚 RescateTMO (Chrome & Selenium Edition)

RescateTMO es una herramienta automatizada en Python diseñada para recuperar, unificar y organizar tu progreso de lectura de manga. Además de analizar tu historial local, también se sincroniza directamente con tu cuenta de Nakamasweb mediante automatización real del navegador usando Selenium.

🛠️ Requisitos Previos

1. Python

Descárgalo desde python.org. En Windows, marca la casilla “Add Python to PATH” durante la instalación.

2. Google Chrome

El script utiliza Selenium para emular un usuario real, por lo que necesitas tener instalado Google Chrome.

3. Instalación de Dependencias

Ejecuta en la terminal dentro de la carpeta del proyecto:
```
python -m pip install selenium webdriver-manager python-dotenv
```
🚀 Configuración y Uso

1. Configurar Credenciales (.env)

Busca el archivo .env.example en el proyecto.

Cópialo y renómbralo a .env.

Rellena tus datos:
```markdown
```text
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

📄 Resultado

Se generará un archivo MIS_MANGAS_RESCATADOS.txt con tu información organizada, por ejemplo:

--- REPORTE DE RESCATE (Total: X mangas) ---

[Leídos] - Berserk
[Pendientes] - Chainsaw Man
[Siguiendo] - One Punch Man
[Solo Historial] - Gantz (Cap 150.0)

⚠️ Privacidad y Seguridad

El archivo .env contiene tu contraseña. Nunca lo compartas.

.gitignore está configurado para ignorar credenciales e historiales.

Todo el proceso ocurre localmente. No se envía información a terceros.

⚖️ Licencia

Este proyecto está bajo la Licencia MIT.
