import sqlite3
import os
import re
import config
import shutil
import requests
from bs4 import BeautifulSoup
import time
import json

# --- CONFIGURACIÓN NAKAMAS ---
EMAIL = config.EMAIL
PASSWORD = config.PASSWORD
URL_BASE = "https://zonatmo.nakamasweb.com"

SECCIONES = {
    "Leídos": f"{URL_BASE}/profile/read",
    "Pendientes": f"{URL_BASE}/profile/pending",
    "Siguiendo": f"{URL_BASE}/profile/follow",
    "Deseados": f"{URL_BASE}/profile/wish",
    "Lo tengo": f"{URL_BASE}/profile/have",
    "Abandonados": f"{URL_BASE}/profile/abandoned"
}

def limpiar_nombre_tmo(titulo):
    if not titulo: return None
    titulo = re.sub(r" - Capítulo \d+.*", "", titulo, flags=re.IGNORECASE)
    titulo = titulo.split(" | ZonaTMO")[0]
    titulo = titulo.split(" - ZonaTMO")[0]
    return titulo.rstrip(" -#").strip()

def iniciar_sesion():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'})
    try:
        res = session.get(f"{URL_BASE}/login")
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find('input', {'name': '_token'})['value']
        payload = {'_token': token, 'email': EMAIL, 'password': PASSWORD, 'remember': 'on'}
        post_res = session.post(f"{URL_BASE}/login", data=payload)
        return session if "profile" in post_res.url else None
    except: return None

def extraer_nakamas(session, nombre_seccion, url_inicial):
    url_actual = url_inicial
    mangas = {}
    print(f" [+] Extrayendo Nakamas ({nombre_seccion})...")
    while url_actual:
        res = session.get(url_actual)
        soup = BeautifulSoup(res.text, 'html.parser')
        for item in soup.select('div.element.proyect-item'):
            titulo_tag = item.select_one('.thumbnail-title')
            if titulo_tag:
                nombre = titulo_tag.get_text(strip=True)
                id_m = re.sub(r'[^a-z0-9]', '', nombre.lower())
                mangas[id_m] = {'nombre': nombre, 'estado': nombre_seccion}
        btn_next = soup.select_one('a[rel="next"]')
        url_actual = btn_next['href'] if btn_next else None
        if url_actual: time.sleep(1)
    return mangas

def procesar_db_local(ruta_db, tipo_navegador):
    archivo_temp = f"temp_{tipo_navegador}"
    progreso_local = {}
    if not os.path.exists(ruta_db): return {}
    
    try:
        shutil.copy2(ruta_db, archivo_temp)
        conn = sqlite3.connect(archivo_temp)
        cursor = conn.cursor()
        # Opera usa la misma estructura que Chrome ('urls')
        query = "SELECT url, title FROM urls WHERE url LIKE '%zonatmo.com/%'" if tipo_navegador in ["CHROME", "OPERA"] else \
                "SELECT url, title FROM moz_places WHERE url LIKE '%zonatmo.com/%'"
        cursor.execute(query)
        for url, titulo in cursor.fetchall():
            if not titulo: continue
            num_cap = 0.0
            match_cap = re.search(r"Capítulo (\d+\.?\d*)", titulo)
            if match_cap:
                try: num_cap = float(match_cap.group(1))
                except: pass
            nombre = limpiar_nombre_tmo(titulo)
            if not nombre or "zonatmo.com" in nombre.lower(): continue
            id_m = re.sub(r'[^a-z0-9]', '', nombre.lower())
            if id_m not in progreso_local or num_cap > progreso_local[id_m]['cap']:
                progreso_local[id_m] = {'nombre': nombre, 'cap': num_cap}
        conn.close()
        os.remove(archivo_temp)
    except Exception as e: print(f" [!] Error DB {tipo_navegador}: {e}")
    return progreso_local

def sync_total():
    print("=== INICIANDO RESCATE TOTAL (OPERA EDITION) ===\n")
    
    # 1. PARTE LOCAL (Búsqueda multicanal)
    todo_el_progreso = {}
    user_path = os.path.expanduser('~')
    
    posibles_rutas = [
        ("History", "CHROME"),
        ("places.sqlite", "FIREFOX"),
        # Rutas comunes de Opera y Opera GX
        (os.path.join(user_path, "AppData/Roaming/Opera Software/Opera Stable/History"), "OPERA"),
        (os.path.join(user_path, "AppData/Roaming/Opera Software/Opera GX Stable/History"), "OPERA"),
        ("History", "OPERA") # Por si lo copiaste a la carpeta del script
    ]
    
    for ruta, tipo in posibles_rutas:
        if os.path.exists(ruta):
            print(f" [+] Detectado historial de {tipo} en: {ruta}")
            datos = procesar_db_local(ruta, tipo)
            for id_m, info in datos.items():
                if id_m not in todo_el_progreso or info['cap'] > todo_el_progreso[id_m].get('cap', 0):
                    todo_el_progreso[id_m] = info

    # 2. PARTE NAKAMASWEB
    sesion = iniciar_sesion()
    if sesion:
        print(" [!] Login exitoso en Nakamasweb.")
        for nombre_sec, url_sec in SECCIONES.items():
            datos_naka = extraer_nakamas(sesion, nombre_sec, url_sec)
            for id_m, info in datos_naka.items():
                if id_m in todo_el_progreso:
                    todo_el_progreso[id_m]['estado'] = nombre_sec
                else:
                    todo_el_progreso[id_m] = {'nombre': info['nombre'], 'cap': 0.0, 'estado': nombre_sec}
    else:
        print(" [X] No se pudo conectar a Nakamasweb.")

    # 3. GENERAR REPORTE
    with open("RESCATE_TOTAL_MANGA.txt", "w", encoding="utf-8") as f:
        f.write("--- REPORTE DE RESCATE UNIFICADO ---\n\n")
        f.write(f"{'ESTADO':<15} | {'CAP':<7} | {'TÍTULO'}\n")
        f.write("-" * 70 + "\n")
        for id_m in sorted(todo_el_progreso):
            info = todo_el_progreso[id_m]
            f.write(f"{info.get('estado', 'Solo Historial'):<15} | {info.get('cap', 0.0):>6.1f}  | {info['nombre']}\n")

    print(f"\n [3/3] ¡LISTO! Reporte generado.")

if __name__ == "__main__":
    sync_total()