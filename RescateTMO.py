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

# --- CONFIGURACIÓN ---
load_dotenv()
EMAIL = os.getenv("USER_EMAIL")
PASSWORD = os.getenv("USER_PASS")
URL_BASE = "https://zonatmo.nakamasweb.com"
ARCHIVO_SALIDA = "MIS_MANGAS_RESCATADOS.txt"

def iniciar_sesion_web():
    """Extrae mangas directamente de la cuenta de Nakamasweb."""
    if not EMAIL or not PASSWORD:
        print(" [!] No hay credenciales en .env. Saltando rescate web.")
        return {}

    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    mangas_web = {}

    try:
        driver.get(f"{URL_BASE}/login")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        print("\n" + "="*50 + "\n [!] Resuelve el CAPTCHA y pulsa ACCEDER...\n" + "="*50)
        wait.until(lambda d: "/login" not in d.current_url)

        secciones = ["read", "pending", "follow", "abandoned"]
        for sec in secciones:
            driver.get(f"{URL_BASE}/profile/{sec}")
            while True:
                time.sleep(2)
                items = driver.find_elements(By.CSS_SELECTOR, "div.element.proyect-item")
                for item in items:
                    titulo = item.find_element(By.CSS_SELECTOR, ".thumbnail-title").text.strip()
                    if titulo not in mangas_web: 
                        mangas_web[titulo] = {"cap": 0.0, "fuentes": {"Web"}}
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
                    driver.execute_script("arguments[0].click();", next_btn)
                except: break
        driver.quit()
    except Exception as e:
        print(f" [X] Error en web: {e}")
    return mangas_web

def extraer_de_historiales():
    """Busca en archivos locales y detecta el tipo de navegador."""
    mangas_locales = {}
    fuentes = {
        "History": ("Chrome/Opera", "SELECT title FROM urls WHERE url LIKE '%zonatmo.com/viewer/%' OR url LIKE '%nakamasweb.com/viewer/%'"),
        "places.sqlite": ("Firefox", "SELECT title FROM moz_places WHERE url LIKE '%zonatmo.com/viewer/%' OR url LIKE '%nakamasweb.com/viewer/%'")
    }

    for archivo, (nombre_nav, query) in fuentes.items():
        if os.path.exists(archivo):
            temp_db = f"temp_{archivo}.db"
            shutil.copyfile(archivo, temp_db)
            try:
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute(query)
                for row in cursor.fetchall():
                    full_title = row[0]
                    if not full_title: continue
                    
                    match = re.search(r'(.*?)\s+Capítulo\s+(\d+\.?\d*)', full_title)
                    if match:
                        nombre, cap = match.group(1).strip(), float(match.group(2))
                    else:
                        nombre, cap = full_title.split('-')[0].strip(), 0.0
                    
                    if nombre not in mangas_locales:
                        mangas_locales[nombre] = {"cap": cap, "fuentes": {nombre_nav}}
                    else:
                        mangas_locales[nombre]["fuentes"].add(nombre_nav)
                        if cap > mangas_locales[nombre]["cap"]:
                            mangas_locales[nombre]["cap"] = cap
                conn.close()
            finally:
                if os.path.exists(temp_db): os.remove(temp_db)
    return mangas_locales

def ejecutar_rescate_total():
    print("=== INICIANDO RESCATE TMO) ===\n")
    
    # Obtener datos de ambas fuentes
    datos_web = iniciar_sesion_web()
    datos_locales = extraer_de_historiales()

    # Combinar diccionarios
    final_dict = datos_web.copy()
    for nombre, info in datos_locales.items():
        if nombre not in final_dict:
            final_dict[nombre] = info
        else:
            # Si ya existe, unimos las fuentes y actualizamos el capítulo si es mayor
            final_dict[nombre]["fuentes"].update(info["fuentes"])
            if info["cap"] > final_dict[nombre]["cap"]:
                final_dict[nombre]["cap"] = info["cap"]

    # Generar el reporte final
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(f"{'FUENTE':<15} | {'ESTADO':<15} | {'CAP':>6} | {'NOMBRE DEL MANGA'}\n")
        f.write("-" * 90 + "\n")
        
        for nombre in sorted(final_dict.keys()):
            info = final_dict[nombre]
            cap = info["cap"]
            fuentes_lista = list(info["fuentes"])
            
            # Lógica de origen: si hay más de una fuente, poner "Multi-Fuente"
            origen = "Multi-Fuente" if len(fuentes_lista) > 1 else fuentes_lista[0]
            estado = "Siguiendo" if cap > 0.0 else "Pendientes"
            
            f.write(f"{origen:<15} | {estado:<15} | {cap:>6.1f} | {nombre}\n")

    print(f"\n [!!!] PROCESO COMPLETADO. Archivo: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    ejecutar_rescate_total()