import os
import re
import time
from dotenv import load_dotenv # Importación necesaria
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CARGAR CONFIGURACIÓN DESDE .ENV ---
load_dotenv()
EMAIL = os.getenv("USER_EMAIL")
PASSWORD = os.getenv("USER_PASS")

if not EMAIL or not PASSWORD:
    print(" [!] ERROR: No se encontraron las credenciales en el archivo .env")
    print(" Asegúrate de tener un archivo .env con USER_EMAIL y USER_PASS")
    exit() # Detiene el script si no hay datos

URL_BASE = "https://zonatmo.nakamasweb.com"

def iniciar_sesion_chrome():
    print(f" [+] Iniciando Google Chrome para: {EMAIL}")
    
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(f"{URL_BASE}/login")

        print(" [+] Rellenando credenciales...")
        wait = WebDriverWait(driver, 20)
        
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(EMAIL)
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(PASSWORD)
        
        print("\n" + "="*50)
        print(" [!] ATENCIÓN: Resuelve el CAPTCHA si aparece.")
        print(" [!] Haz clic en 'ACCEDER' manualmente.")
        print("="*50 + "\n")
        
        wait.until(lambda d: "/login" not in d.current_url)
        
        print(f" [+] Login exitoso detectado.")
        return driver

    except Exception as e:
        print(f" [X] Error durante el inicio: {e}")
        return None

def extraer_seccion(driver, url_seccion, nombre_seccion):
    mangas = {}
    driver.get(url_seccion)
    print(f" [+] Extrayendo sección: {nombre_seccion}...")

    while True:
        time.sleep(2.5) 
        items = driver.find_elements(By.CSS_SELECTOR, "div.element.proyect-item")
        
        for item in items:
            try:
                titulo_el = item.find_element(By.CSS_SELECTOR, ".thumbnail-title")
                titulo = titulo_el.text.strip()
                id_m = re.sub(r'[^a-z0-9]', '', titulo.lower())
                mangas[id_m] = {'nombre': titulo, 'estado': nombre_seccion}
            except:
                continue

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            driver.execute_script("arguments[0].click();", next_btn)
            print(f"   ... pasando página en {nombre_seccion}")
        except:
            break 
            
    return mangas

def ejecutar_rescate_total():
    print("=== RESCATE DE MANGAS (MODO .ENV + CHROME) ===\n")
    
    driver = iniciar_sesion_chrome()
    if not driver:
        return

    todo_el_progreso = {}
    
    secciones_a_escanear = {
        "Leídos": f"{URL_BASE}/profile/read",
        "Pendientes": f"{URL_BASE}/profile/pending",
        "Siguiendo": f"{URL_BASE}/profile/follow",
        "Abandonados": f"{URL_BASE}/profile/abandoned"
    }

    for nombre, url in secciones_a_escanear.items():
        datos_seccion = extraer_seccion(driver, url, nombre)
        todo_el_progreso.update(datos_seccion)
        print(f" [OK] {len(datos_seccion)} mangas guardados de {nombre}.")

    driver.quit()

    archivo_final = "MIS_MANGAS_RESCATADOS.txt"
    with open(archivo_final, "w", encoding="utf-8") as f:
        f.write(f"--- REPORTE DE RESCATE (Total: {len(todo_el_progreso)} mangas) ---\n\n")
        for id_m in sorted(todo_el_progreso):
            info = todo_el_progreso[id_m]
            f.write(f"[{info['estado']}] {info['nombre']}\n")

    print(f"\n [!!!] PROCESO TERMINADO. Archivo: {archivo_final}")

if __name__ == "__main__":
    ejecutar_rescate_total()