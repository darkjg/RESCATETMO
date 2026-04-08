import sqlite3
import os
import re
import shutil

def limpiar_nombre_tmo(titulo):
    if not titulo: return None
    titulo = re.sub(r" - Capítulo \d+.*", "", titulo, flags=re.IGNORECASE)
    titulo = titulo.split(" | ZonaTMO")[0]
    titulo = titulo.split(" - ZonaTMO")[0]
    return titulo.rstrip(" -#").strip()

def procesar_db(ruta_db, tipo_navegador):
    """ Función genérica para extraer datos según el navegador """
    archivo_temp = f"temp_{tipo_navegador}"
    progreso_local = {}
    
    try:
        # Copia temporal para evitar bloqueos si el navegador está abierto
        shutil.copy2(ruta_db, archivo_temp)
        conn = sqlite3.connect(archivo_temp)
        cursor = conn.cursor()
        
        # Ajustar query según el navegador
        if tipo_navegador == "CHROME":
            query = "SELECT url, title FROM urls WHERE url LIKE '%zonatmo.com/%'"
        else: # FIREFOX
            query = "SELECT url, title FROM moz_places WHERE url LIKE '%zonatmo.com/%'"
            
        cursor.execute(query)
        for url, titulo in cursor.fetchall():
            if not titulo: continue
            
            # 1. Extraer capítulo
            num_cap = 0.0
            match_cap = re.search(r"Capítulo (\d+\.?\d*)", titulo)
            if match_cap:
                try: num_cap = float(match_cap.group(1))
                except: pass

            # 2. Limpiar nombre
            nombre = limpiar_nombre_tmo(titulo)
            if not nombre or "zonatmo.com" in nombre.lower(): continue
            
            # 3. Guardar/Comparar
            id_m = re.sub(r'[^a-z0-9]', '', nombre.lower())
            if id_m not in progreso_local or num_cap > progreso_local[id_m][1]:
                progreso_local[id_m] = [nombre, num_cap]
        
        conn.close()
        os.remove(archivo_temp)
        return progreso_local
    except Exception as e:
        print(f" [!] Error procesando {tipo_navegador}: {e}")
        return {}

def ejecutar_super_detector():
    dbs_encontradas = []
    # Posibles nombres de archivos
    if os.path.exists("places.sqlite"): dbs_encontradas.append(("places.sqlite", "FIREFOX"))
    if os.path.exists("History"): dbs_encontradas.append(("History", "CHROME"))

    if not dbs_encontradas:
        print(" [X] No se detectó ninguna base de datos en la carpeta.")
        print(" [!] Debes copiar 'places.sqlite' (Firefox) o 'History' (Chrome) aquí.")
        return

    todo_el_progreso = {} # {id: [nombre, cap]}

    for ruta, tipo in dbs_encontradas:
        print(f" [+] Detectado {tipo}. Extrayendo datos...")
        datos = procesar_db(ruta, tipo)
        
        # Fusionar datos encontrados con los globales (quedarse siempre con el cap más alto)
        for id_m, info in datos.items():
            if id_m not in todo_el_progreso or info[1] > todo_el_progreso[id_m][1]:
                todo_el_progreso[id_m] = info

    # Escribir resultado final
    archivo_final = "LISTA_TMO.txt"
    with open(archivo_final, "w", encoding="utf-8") as f:
        f.write(f"--- LISTA TMO (Detección Auto: {[t for r,t in dbs_encontradas]}) ---\n\n")
        for nombre, cap in sorted(todo_el_progreso.values(), key=lambda x: x[0]):
            f.write(f"[{cap:06.2f}] - {nombre}\n")

    print(f"\n [3/3] ¡PROCESO FINALIZADO!")
    print(f" [>] Obras totales: {len(todo_el_progreso)}")
    print(f" [>] Archivo: {archivo_final}")

if __name__ == "__main__":
    ejecutar_super_detector()