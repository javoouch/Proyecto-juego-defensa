# /gui/main_gui.py
import pygame
import sys
import os
import time
import logging # Importar el módulo de logging [cite: 356]

# --- Añadir la carpeta raíz al path para encontrar 'src' ---
script_dir = os.path.dirname(__file__) 
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# --- Configuración del Logging (Fase 3) --- [cite: 348]
# Define la ruta del archivo de log usando la nueva carpeta /logs 
log_file_path = os.path.join(project_root, 'logs', 'logs.txt')
# Configura el logging para que escriba en el archivo
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO, # Nivel de registro (INFO y superior)
    format='%(asctime)s - %(levelname)s - %(message)s', # Formato de cada línea
    filemode='w' # 'w' sobrescribe el log cada vez, 'a' lo añade al final
)
log = logging.getLogger(__name__)
log.info("--- Aplicación iniciada ---") # [cite: 349]

# --- Importar funciones del algoritmo A* ---
try:
    from algoritmo_a_estrella import cargar_datos, buscar_camino, calcular_heuristica_manhattan
except ImportError as e:
    log.error(f"Error crítico al importar 'algoritmo_a_estrella.py': {e}")
    print(f"Error al importar: {e}")
    sys.exit(1)

# --- Configuración de Pygame y Colores ---
try:
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    log.info("Pygame inicializado correctamente.")
except pygame.error as e:
    log.error(f"Error inicializando Pygame: {e}")
    print(f"Error inicializando Pygame: {e}")
    sys.exit(1)

TAMANO_CELDA = 25
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)     # Obstáculos
VERDE = (0, 255, 0)   # Camino
AZUL = (0, 0, 255)    # Inicio
AMARILLO = (255, 255, 0) # Fin
GRIS = (200, 200, 200) # Grid
FUENTE_TAM = 20

# --- Variables Globales ---
mapa_cargado = None
nombre_mapa_actual = ""
inicio_pos = None
fin_pos = None
camino_encontrado = None
nodos_explorados = 0
tiempo_ejecucion = 0
largo_camino = 0
pantalla = None
mensaje_estado = "Presiona 'L' para cargar mapa (se pedirá en terminal)"
filas, columnas = 0, 0
ruta_resultados_csv = os.path.join(project_root, 'results', 'experimentos.csv') 

# --- Funciones de la GUI ---

def pedir_nombre_archivo_terminal():
    # ... (Sin cambios, esta función ya maneja la selección) ...
    print("\n--- Cargar Mapa ---")
    ruta_data = os.path.join(project_root, 'data')
    print(f"Archivos disponibles en '{ruta_data}':")
    try:
        archivos_txt = [f for f in os.listdir(ruta_data) if f.endswith('.txt')]
        if not archivos_txt:
            print("  (No se encontraron archivos .txt)")
            return None, None
        for archivo in archivos_txt:
            print(f"  - {archivo}")
    except FileNotFoundError:
        log.error(f"La carpeta 'data' no existe en {ruta_data}")
        print(f"  Error: La carpeta '{ruta_data}' no existe.")
        return None, None
        
    nombre_archivo = input("Escribe el nombre del archivo (ej: caso_base.txt): ")
    ruta_relativa = os.path.join('data', nombre_archivo) 
    ruta_completa_test = os.path.join(project_root, ruta_relativa)
    
    if not os.path.exists(ruta_completa_test):
        log.warning(f"Intento de carga fallido. Archivo no encontrado: {nombre_archivo}")
        print(f"Advertencia: El archivo '{nombre_archivo}' no existe.")
        return None, None
        
    return ruta_relativa, nombre_archivo

def dibujar_grid(pantalla, filas, columnas):
    # ... (Sin cambios) ...
    if not pantalla or filas <= 0 or columnas <= 0: return 
    ancho_total = columnas * TAMANO_CELDA
    alto_total = filas * TAMANO_CELDA
    for x in range(0, ancho_total + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, GRIS, (x, 0), (x, alto_total))
    for y in range(0, alto_total + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, GRIS, (0, y), (ancho_total, y))

def dibujar_mapa(pantalla, mapa):
    # ... (Sin cambios) ...
    if not pantalla or not mapa: return
    filas_mapa = len(mapa)
    columnas_mapa = len(mapa[0])
    for fila in range(filas_mapa):
        for columna in range(columnas_mapa):
            color = BLANCO
            char = mapa[fila][columna]
            if char == 'X': color = ROJO
            elif char == 'S': color = AZUL
            elif char == 'E': color = AMARILLO

            pygame.draw.rect(pantalla, color, (columna * TAMANO_CELDA, fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA))

def dibujar_camino(pantalla, camino):
    # ... (Sin cambios) ...
    if not pantalla or not camino: return
    for (fila, columna) in camino[1:-1]: 
         pygame.draw.rect(pantalla, VERDE,
                         (columna * TAMANO_CELDA + 2, fila * TAMANO_CELDA + 2,
                          TAMANO_CELDA - 4, TAMANO_CELDA - 4)) 

def mostrar_texto(pantalla, texto, posicion, color=NEGRO):
    # ... (Sin cambios) ...
    if not pantalla: return
    try:
        fuente = pygame.font.SysFont(None, FUENTE_TAM) 
        superficie_texto = fuente.render(texto, True, color)
        pantalla.blit(superficie_texto, posicion)
    except Exception as e:
        log.error(f"Error al mostrar texto: {e}")
        print(f"Error al mostrar texto: {e}")

def guardar_resultado_csv(ruta_archivo, nombre_mapa, estrategia, tiempo, nodos, largo):
    # ... (Sin cambios, esta función ya funciona como un log de métricas) ... [cite: 347]
    encabezado = "Mapa,Estrategia,Tiempo_Ejecucion_s,Nodos_Explorados,Largo_Camino_Solucion\n"
    linea = f"{nombre_mapa},{estrategia},{tiempo:.6f},{nodos},{largo}\n"
    
    try:
        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'w') as f:
                f.write(encabezado)
        
        with open(ruta_archivo, 'a') as f:
            f.write(linea)
        log.info(f"Resultado CSV guardado: {linea.strip()}")
    except Exception as e:
        log.error(f"Error al guardar CSV: {e}")
        print(f"Error al guardar CSV: {e}")

def ejecutar_experimento(estrategia):
    """Función para ejecutar el algoritmo y actualizar el estado."""
    global camino_encontrado, nodos_explorados, tiempo_ejecucion, largo_camino, mensaje_estado
    
    # Validación para evitar ejecución sin datos cargados [cite: 331]
    if not (mapa_cargado and inicio_pos and fin_pos):
        mensaje_estado = "Error: Carga un mapa válido (con S y E) primero usando 'L'."
        log.warning("Intento de ejecución sin mapa cargado.")
        print(mensaje_estado)
        return

    mensaje_estado = f"Ejecutando {estrategia.upper()}..."
    print(mensaje_estado)
    actualizar_pantalla() 
    
    start_time = time.time() # Log de tiempo inicio [cite: 349]
    camino_encontrado, nodos, largo = buscar_camino(mapa_cargado, inicio_pos, fin_pos, estrategia)
    end_time = time.time()
    
    tiempo_ejecucion = end_time - start_time
    nodos_explorados = nodos
    
    # Mensajes amigables [cite: 340-342]
    if camino_encontrado:
        largo_camino = largo 
        mensaje_estado = f"{estrategia.upper()} OK! Pasos:{largo} Nodos:{nodos} T:{tiempo_ejecucion:.4f}s"
    else:
        largo_camino = -1 
        mensaje_estado = f"No se encontró ruta para {estrategia.upper()}. Nodos:{nodos} T:{tiempo_ejecucion:.4f}s"
    
    print(mensaje_estado)
    # Guardar en CSV (que también funciona como log de métricas)
    guardar_resultado_csv(ruta_resultados_csv, nombre_mapa_actual, estrategia, tiempo_ejecucion, nodos_explorados, largo_camino)
    # Guardar en log principal [cite: 358-360]
    log.info(f"Ejecución finalizada. {mensaje_estado}")


def resetear_escenario():
    """Limpia el camino y los resultados, pero mantiene el mapa cargado."""
    global camino_encontrado, nodos_explorados, tiempo_ejecucion, largo_camino, mensaje_estado
    
    camino_encontrado = None
    nodos_explorados = 0
    tiempo_ejecucion = 0
    largo_camino = 0
    mensaje_estado = f"Mapa '{nombre_mapa_actual}' reiniciado. Elige algoritmo."
    log.info(f"Escenario '{nombre_mapa_actual}' reiniciado por el usuario.")
    print(mensaje_estado)


def actualizar_pantalla():
    """Función centralizada para dibujar todo."""
    if not pantalla: return
    
    pantalla.fill(BLANCO)
    
    if mapa_cargado and filas > 0 and columnas > 0:
        dibujar_mapa(pantalla, mapa_cargado)
        dibujar_camino(pantalla, camino_encontrado) 
        dibujar_grid(pantalla, filas, columnas)
        # Mostrar métricas y estado (resumen en pantalla) [cite: 366]
        mostrar_texto(pantalla, mensaje_estado, (10, filas * TAMANO_CELDA + 10))
        # Instrucciones (Etiquetas explicativas) [cite: 376]
        mostrar_texto(pantalla, "[L] Cargar | [1] Dijkstra | [2] A* | [3] Greedy | [R] Reiniciar", (10, filas * TAMANO_CELDA + 30), (50, 50, 50))
    else:
         mostrar_texto(pantalla, "Presiona 'L' (mira la terminal) para cargar un mapa.", (10, 10))
         mostrar_texto(pantalla, mensaje_estado, (10, 40)) 

    try:
        pygame.display.flip() 
    except pygame.error as e:
         log.error(f"Error al actualizar pantalla (pygame.display.flip): {e}")
         print(f"Error al actualizar pantalla (pygame.display.flip): {e}")


def main():
    global mapa_cargado, inicio_pos, fin_pos, camino_encontrado, nodos_explorados, tiempo_ejecucion, pantalla, mensaje_estado, filas, columnas, nombre_mapa_actual, largo_camino

    ancho_inicial, alto_inicial = 600, 450
    try:
        pantalla = pygame.display.set_mode((ancho_inicial, alto_inicial), pygame.RESIZABLE)
        pygame.display.set_caption("Lab 30: Release Candidate")
    except pygame.error as e:
        log.critical(f"Error CRÍTICO al inicializar Pygame display: {e}")
        print(f"Error CRÍTICO al inicializar Pygame display: {e}")
        sys.exit(1)

    ejecutando = True
    while ejecutando:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            if evento.type == pygame.VIDEORESIZE:
                 nuevo_ancho, nuevo_alto = evento.w, evento.h
                 alto_minimo = alto_inicial 
                 if filas > 0: alto_minimo = filas * TAMANO_CELDA + 60 
                 alto_final = max(nuevo_alto, alto_minimo) 
                 ancho_final = max(nuevo_ancho, ancho_inicial if columnas == 0 else columnas * TAMANO_CELDA)
                 try:
                     pantalla = pygame.display.set_mode((ancho_final, alto_final), pygame.RESIZABLE)
                 except pygame.error: pass 

            if evento.type == pygame.KEYDOWN:
                 if evento.key == pygame.K_l: 
                    ruta_relativa, nombre_base = pedir_nombre_archivo_terminal()
                    if ruta_relativa:
                        # La función cargar_datos ahora devuelve 4 valores
                        mapa_cargado, inicio_pos, fin_pos, msg = cargar_datos(ruta_relativa)
                        mensaje_estado = msg # Mensaje amigable [cite: 340-342]
                        
                        if mapa_cargado and inicio_pos and fin_pos:
                            nombre_mapa_actual = nombre_base
                            filas = len(mapa_cargado)
                            columnas = len(mapa_cargado[0])
                            ancho_pantalla = columnas * TAMANO_CELDA
                            alto_pantalla = filas * TAMANO_CELDA + 60 
                            pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)
                            camino_encontrado = None
                        else:
                            mapa_cargado = None; filas = 0; columnas = 0
                            log.warning(f"Carga fallida para '{ruta_relativa}'. Mensaje: {msg}")
                    else:
                         mensaje_estado = "Carga cancelada o archivo no encontrado."
                 
                 elif evento.key == pygame.K_1: 
                    ejecutar_experimento("dijkstra")
                 
                 elif evento.key == pygame.K_2: 
                    ejecutar_experimento("a_estrella")
                 
                 elif evento.key == pygame.K_3: 
                    ejecutar_experimento("greedy")
                
                 # Fase 4: Añadir botón de reiniciar 
                 elif evento.key == pygame.K_r:
                    if mapa_cargado:
                        resetear_escenario()
                    else:
                        mensaje_estado = "No hay nada que reiniciar. Carga un mapa con 'L'."

        actualizar_pantalla()

    log.info("--- Aplicación cerrada ---")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()