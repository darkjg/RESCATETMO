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

📄 Formato del Reporte (MIS_MANGAS_RESCATADOS.txt)

El archivo de salida utiliza un formato de tabla limpia con las siguientes reglas:
```text
FUENTE          | ESTADO          |  CAP  | NOMBRE DEL MANGA
----------------------------------------------------------------------------------
Multi-Fuente    | Siguiendo       |  45.0 | Ejemplo de manga en Web e Historial
Web             | Pendientes      |   0.0 | Ejemplo de manga solo en Nakamasweb
Chrome/Opera    | Siguiendo       |  12.5 | Ejemplo de manga solo en el navegador
```
💡 Características Especiales:

    Consolidación de Nombres: Si un manga aparece en varias fuentes, solo verás una línea.

    Origen "Multi-Fuente": Esta etiqueta indica que el manga se encontró en más de un sitio (ej: Web + Firefox).

    Capítulo Inteligente: El script compara todos los registros y se queda siempre con el capítulo más alto encontrado.

    Clasificación por Capítulo: * CAP > 0.0 ➜ Siguiendo

        CAP = 0.0 ➜ Pendientes

⚠️ Privacidad y Seguridad

El archivo .env contiene tu contraseña. Nunca lo compartas.

.gitignore está configurado para ignorar credenciales e historiales.

Todo el proceso ocurre localmente. No se envía información a terceros.

⚖️ Licencia

Este proyecto está bajo la Licencia MIT.
