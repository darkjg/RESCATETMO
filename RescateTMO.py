import os
import re
import time
import sqlite3
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
EMAIL = os.getenv("USER_EMAIL")
PASSWORD = os.getenv("USER_PASS")
URL_BASE = "https://zonatmo.nakamasweb.com"
ARCHIVO_SALIDA = "MIS_MANGAS_RESCATADOS.txt"

def ejecutar_rescate():
    if not EMAIL or not PASSWORD:
        print(" [!] ERROR: Credenciales no encontradas en .env")
        return

    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    mangas_finales = {}

    try:
        driver.get(f"{URL_BASE}/login")
        
        # Rellenar datos automáticamente
        print(" [+] Rellenando credenciales...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        print("\n" + "!"*60)
        print(" 1. Resuelve el CAPTCHA en la ventana de Chrome.")
        print(" 2. Haz clic en ACCEDER.")
        print(" 3. Una vez veas TU PERFIL, vuelve aquí y PULSA ENTER.")
        print("!"*60 + "\n")
        
        # ESTO ES LO QUE CAMBIA: El script se para hasta que tú le des al ENTER en la consola
        input(" >>> ¿Ya has logueado correctamente? Presiona ENTER para continuar...")

        secciones = {
            "read": "leido",
            "pending": "pendiente",
            "follow": "siguiendo",
            "wish": "favorito",
            "have": "lo tengo",
            "abandoned": "abandonado"
        }

        for path, tag in secciones.items():
            print(f" [+] Extrayendo sección web: {tag.upper()}...")
            driver.get(f"{URL_BASE}/profile/{path}")
            time.sleep(4) # Espera generosa para carga

            while True:
                items = driver.find_elements(By.CSS_SELECTOR, "div.element.proyect-item")
                for item in items:
                    try:
                        titulo = item.find_element(By.CSS_SELECTOR, ".thumbnail-title").text.strip()
                        if titulo and titulo not in mangas_finales:
                            mangas_finales[titulo] = {"cap": 0.0, "fuentes": {"Web"}, "estado": tag}
                    except: continue
                
                # Intentar avanzar página
                try:
                    next_btn = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
                    if next_btn:
                        driver.execute_script("arguments[0].click();", next_btn[0])
                        time.sleep(3)
                    else: break
                except: break
        
        driver.quit()

    except Exception as e:
        print(f" [!] Nota: Interrupción en la parte web: {e}")

    # --- PROCESAR HISTORIAL LOCAL (Tus 154 mangas) ---
    print("\n [+] Analizando bases de datos locales...")
    locales = extraer_de_historiales()
    for nom, info in locales.items():
        if nom not in mangas_finales:
            mangas_finales[nom] = info
        else:
            mangas_finales[nom]["fuentes"].update(info["fuentes"])
            if info["cap"] > mangas_finales[nom]["cap"]:
                mangas_finales[nom]["cap"] = info["cap"]
                if info["cap"] > 0:
                    mangas_finales[nom]["estado"] = "leyendo"

    # --- GUARDAR REPORTE ---
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(f"{'FUENTE':<18} | {'ESTADO':<12} | {'CAP':>6} | {'NOMBRE DEL MANGA'}\n")
        f.write("-" * 100 + "\n")
        for nom in sorted(mangas_finales.keys()):
            inf = mangas_finales[nom]
            org = "Multi-Fuente" if len(inf["fuentes"]) > 1 else list(inf["fuentes"])[0]
            f.write(f"{org:<18} | {inf['estado']:<12} | {inf['cap']:>6.1f} | {nom}\n")

    print(f"\n [!!!] PROCESO FINALIZADO.")
    print(f" [>] Total consolidado: {len(mangas_finales)} mangas.")

def extraer_de_historiales():
    mangas_locales = {}
    fuentes = {
        "History": ("Chrome/Opera/Edge", "SELECT title FROM urls WHERE url LIKE '%zonatmo.com/viewer/%' OR url LIKE '%nakamasweb.com/viewer/%'"),
        "places.sqlite": ("Firefox", "SELECT title FROM moz_places WHERE url LIKE '%zonatmo.com/viewer/%' OR url LIKE '%nakamasweb.com/viewer/%'")
    }
    for archivo, (nav, query) in fuentes.items():
        if os.path.exists(archivo):
            temp = f"temp_{archivo}.db"
            shutil.copyfile(archivo, temp)
            try:
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                cursor.execute(query)
                for row in cursor.fetchall():
                    txt = row[0]
                    if not txt: continue
                    match = re.search(r'(.*?)\s+Capítulo\s+(\d+\.?\d*)', txt)
                    nombre, cap = (match.group(1).strip(), float(match.group(2))) if match else (txt.split('-')[0].strip(), 0.0)
                    if nombre not in mangas_locales or cap > mangas_locales[nombre]["cap"]:
                        mangas_locales[nombre] = {"cap": cap, "fuentes": {nav}, "estado": "leyendo" if cap > 0 else "pendiente"}
                conn.close()
            finally:
                if os.path.exists(temp): os.remove(temp)
    return mangas_locales

if __name__ == "__main__":
    ejecutar_rescate()