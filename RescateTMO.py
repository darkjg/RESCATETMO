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
ARCHIVO_SALIDA = "MIS_MANGAS_RESCATADOS_COMPLETO.txt"

def ejecutar_rescate():
    if not EMAIL or not PASSWORD:
        print(" [!] ERROR: Credenciales no encontradas en .env")
        return

    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    mangas_finales = {}

    try:
        driver.get(f"{URL_BASE}/login")
        print(" [+] Rellenando credenciales...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        print("\n" + "!"*60)
        print(" 1. Resuelve el CAPTCHA y logueate.")
        print(" 2. Cuando estés en tu perfil, vuelve aquí y PULSA ENTER.")
        print("!"*60 + "\n")
        input(" >>> ¿Logueado? Presiona ENTER...")

        secciones = {
            "read": "leido",
            "pending": "pendiente",
            "follow": "siguiendo",
            "wish": "favorito",
            "abandoned": "abandonado"
        }

        mangas_a_revisar = []
        
        # --- FASE 1: RECOLECCIÓN DE URLS (Tu lógica original) ---
        for path, tag in secciones.items():
            print(f" [+] Escaneando lista: {tag.upper()}...")
            driver.get(f"{URL_BASE}/profile/{path}")
            time.sleep(3)

            while True:
                items = driver.find_elements(By.CSS_SELECTOR, "div.element.proyect-item")
                for item in items:
                    try:
                        link_el = item.find_element(By.CSS_SELECTOR, "a")
                        url = link_el.get_attribute("href")
                        titulo = item.find_element(By.CSS_SELECTOR, ".thumbnail-title").text.strip()
                        mangas_a_revisar.append((titulo, url, tag))
                    except: continue
                
                try:
                    next_btn = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
                    if next_btn and next_btn[0].is_displayed():
                        driver.execute_script("arguments[0].click();", next_btn[0])
                        time.sleep(3)
                    else: break
                except: break

        # --- FASE 2: INSPECCIÓN (Con botón "Ver todo" y Pausa) ---
        total = len(mangas_a_revisar)
        print(f"\n [+] Analizando {total} mangas. Pausa de 5s entre cada uno...")
        
        for i, (titulo, url, estado) in enumerate(mangas_a_revisar, 1):
            print(f" [{i}/{total}] Revisando: {titulo[:40]}...", end="\r")
            cap_leido = 0.0
            
            try:
                driver.get(url)
                # Esperar a que cargue la zona de capítulos
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "chapters")))
                
                # --- NUEVO: Lógica del botón "Ver todo" ---
                try:
                    # Buscamos el botón ID 'show-chapters' que viste en la imagen
                    boton_ver_todo = driver.find_element(By.ID, "show-chapters")
                    if boton_ver_todo.is_displayed():
                        driver.execute_script("arguments[0].click();", boton_ver_todo)
                        time.sleep(1.5) # Espera a que se desplieguen los ocultos
                except:
                    pass # Si no hay botón, no pasa nada

                # Buscar el ojo azul (clase 'viewed')
                vistos = driver.find_elements(By.XPATH, "//li[contains(@class, 'list-group-item')][descendant::span[contains(@class, 'viewed')]]")
                
                if vistos:
                    texto_cap = vistos[0].find_element(By.TAG_NAME, "h4").text
                    match = re.search(r'(\d+\.?\d*)', texto_cap)
                    if match:
                        cap_leido = float(match.group(1))
                
                mangas_finales[titulo] = {"cap": cap_leido, "fuentes": {"Web"}, "estado": estado}
                
            except Exception:
                mangas_finales[titulo] = {"cap": 0.0, "fuentes": {"Web (Error)"}, "estado": estado}

            time.sleep(5) # PAUSA ANTI-BAN

        driver.quit()

    except Exception as e:
        print(f" [!] Error crítico: {e}")

    # --- FASE 3: HISTORIAL LOCAL (No se borra, se mantiene igual) ---
    print("\n [+] Analizando bases de datos locales (Chrome/Firefox/Edge)...")
    locales = extraer_de_historiales()
    for nom, info in locales.items():
        if nom not in mangas_finales:
            mangas_finales[nom] = info
        else:
            mangas_finales[nom]["fuentes"].update(info["fuentes"])
            if info["cap"] > mangas_finales[nom]["cap"]:
                mangas_finales[nom]["cap"] = info["cap"]

    # --- GUARDAR REPORTE FINAL ---
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(f"{'FUENTE':<18} | {'ESTADO':<12} | {'CAP':>6} | {'NOMBRE DEL MANGA'}\n")
        f.write("-" * 100 + "\n")
        for nom in sorted(mangas_finales.keys()):
            inf = mangas_finales[nom]
            fuente_str = "Multi-Fuente" if len(inf["fuentes"]) > 1 else list(inf["fuentes"])[0]
            f.write(f"{fuente_str:<18} | {inf['estado']:<12} | {inf['cap']:>6.1f} | {nom}\n")

    print(f"\n [!!!] PROCESO FINALIZADO. Archivo: {ARCHIVO_SALIDA}")

def extraer_de_historiales():
    mangas_locales = {}
    fuentes = {
        "History": ("Chrome/Edge", "SELECT title FROM urls WHERE url LIKE '%zonatmo.com/viewer/%' OR url LIKE '%nakamasweb.com/viewer/%'"),
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
                        mangas_locales[nombre] = {"cap": cap, "fuentes": {nav}, "estado": "leyendo"}
                conn.close()
            finally:
                if os.path.exists(temp): os.remove(temp)
    return mangas_locales

if __name__ == "__main__":
    ejecutar_rescate()