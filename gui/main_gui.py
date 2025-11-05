# /gui/main_gui.py
import pygame
import sys
import os
import time

# --- Añadir la carpeta raíz al path para encontrar 'src' ---
script_dir = os.path.dirname(__file__) # Directorio de este script (gui)
project_root = os.path.dirname(script_dir) # Directorio padre (Proyecto_Minijuego)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# --- Importar funciones del algoritmo A* ---
try:
    # Asegúrate que tu archivo en src se llama 'algoritmo_a_estrella.py'
    from algoritmo_a_estrella import cargar_datos, buscar_camino, calcular_heuristica_manhattan
except ImportError as e:
    print(f"Error al importar: {e}")
    print("Asegúrate de que el archivo '/src/algoritmo_a_estrella.py' existe y tiene la función 'buscar_camino'.")
    sys.exit(1)
except Exception as e:
    print(f"Otro error al importar: {e}")
    sys.exit(1)

# --- Configuración de Pygame y Colores ---
pygame.init()
if not pygame.font.get_init():
    pygame.font.init()
    print("--- DEBUG: Pygame font inicializado ---")

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
ruta_resultados = os.path.join(project_root, 'results', 'experimentos.csv') # Ruta para guardar CSV 

# --- Funciones de la GUI ---

def pedir_nombre_archivo_terminal():
    """Pide al usuario el nombre del archivo del mapa en la terminal."""
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
        print(f"  Error: La carpeta '{ruta_data}' no existe.")
        return None, None
        
    nombre_archivo = input("Escribe el nombre del archivo (ej: caso_base.txt): ")
    ruta_relativa = os.path.join('data', nombre_archivo) 
    ruta_completa_test = os.path.join(project_root, ruta_relativa)
    
    if not os.path.exists(ruta_completa_test):
        print(f"Advertencia: El archivo '{nombre_archivo}' no existe.")
        return None, None
        
    return ruta_relativa, nombre_archivo # Devuelve ruta relativa y nombre base

def dibujar_grid(pantalla, filas, columnas):
    """Dibuja las líneas de la cuadrícula."""
    if not pantalla or filas <= 0 or columnas <= 0: return 
    ancho_total = columnas * TAMANO_CELDA
    alto_total = filas * TAMANO_CELDA
    for x in range(0, ancho_total + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, GRIS, (x, 0), (x, alto_total))
    for y in range(0, alto_total + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, GRIS, (0, y), (ancho_total, y))

def dibujar_mapa(pantalla, mapa):
    """Dibuja el mapa cargado con obstáculos, inicio y fin."""
    if not pantalla or not mapa: return
    # ... (Sin cambios respecto a tu código anterior) ...
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
    """Dibuja el camino encontrado (si existe)."""
    if not pantalla or not camino: return
    # ... (Sin cambios respecto a tu código anterior) ...
    for (fila, columna) in camino[1:-1]: 
         pygame.draw.rect(pantalla, VERDE,
                         (columna * TAMANO_CELDA + 2, fila * TAMANO_CELDA + 2,
                          TAMANO_CELDA - 4, TAMANO_CELDA - 4)) 

def mostrar_texto(pantalla, texto, posicion, color=NEGRO):
    """Muestra texto en la pantalla."""
    if not pantalla: return
    try:
        fuente = pygame.font.SysFont(None, FUENTE_TAM) 
        superficie_texto = fuente.render(texto, True, color)
        pantalla.blit(superficie_texto, posicion)
    except Exception as e:
        print(f"Error al mostrar texto: {e}")

def guardar_resultado_csv(ruta_archivo, nombre_mapa, estrategia, tiempo, nodos, largo):
    """Guarda una línea de resultado en el archivo CSV."""
    # 
    encabezado = "Mapa,Estrategia,Tiempo_Ejecucion_s,Nodos_Explorados,Largo_Camino_Solucion\n"
    linea = f"{nombre_mapa},{estrategia},{tiempo:.6f},{nodos},{largo}\n"
    
    try:
        # Si el archivo no existe, crea el encabezado
        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'w') as f:
                f.write(encabezado)
        
        # Añade la nueva línea de resultado
        with open(ruta_archivo, 'a') as f:
            f.write(linea)
        print(f"Resultado guardado en '{ruta_archivo}'")
    except Exception as e:
        print(f"Error al guardar CSV: {e}")

def ejecutar_experimento(estrategia):
    """Función para ejecutar el algoritmo y actualizar el estado."""
    global camino_encontrado, nodos_explorados, tiempo_ejecucion, largo_camino, mensaje_estado
    
    if not (mapa_cargado and inicio_pos and fin_pos):
        mensaje_estado = "Carga un mapa válido (con S y E) primero usando 'L'."
        print(mensaje_estado)
        return

    mensaje_estado = f"Ejecutando {estrategia.upper()}..."
    print(mensaje_estado)
    # Actualiza la pantalla para mostrar el mensaje "Ejecutando..."
    actualizar_pantalla() 
    
    # --- Ejecutar el algoritmo y medir métricas [cite: 326, 328] ---
    start_time = time.time()
    camino_encontrado, nodos, largo = buscar_camino(mapa_cargado, inicio_pos, fin_pos, estrategia)
    end_time = time.time()
    
    # --- Actualizar variables globales ---
    tiempo_ejecucion = end_time - start_time
    nodos_explorados = nodos
    
    if camino_encontrado:
        largo_camino = largo # 
        mensaje_estado = f"{estrategia.upper()} OK! Pasos:{largo} Nodos:{nodos} T:{tiempo_ejecucion:.4f}s"
    else:
        largo_camino = -1 # Indica que no hay solución 
        mensaje_estado = f"{estrategia.upper()} NO ENCONTRÓ CAMINO. Nodos:{nodos} T:{tiempo_ejecucion:.4f}s"
    
    print(mensaje_estado)
    
    # --- Guardar resultado en CSV  ---
    guardar_resultado_csv(ruta_resultados, nombre_mapa_actual, estrategia, tiempo_ejecucion, nodos_explorados, largo_camino)


def actualizar_pantalla():
    """Función centralizada para dibujar todo."""
    if not pantalla: return
    
    pantalla.fill(BLANCO)
    
    if mapa_cargado and filas > 0 and columnas > 0:
        dibujar_mapa(pantalla, mapa_cargado)
        dibujar_camino(pantalla, camino_encontrado) # Dibuja el camino (si existe)
        dibujar_grid(pantalla, filas, columnas)
        # Mostrar mensaje de estado y métricas abajo
        mostrar_texto(pantalla, mensaje_estado, (10, filas * TAMANO_CELDA + 10))
        # Instrucciones de teclas
        mostrar_texto(pantalla, "[L] Cargar | [1] Dijkstra | [2] A* | [3] Greedy", (10, filas * TAMANO_CELDA + 30), (50, 50, 50))
    else:
         mostrar_texto(pantalla, "Presiona 'L' (mira la terminal) para cargar un mapa.", (10, 10))
         mostrar_texto(pantalla, mensaje_estado, (10, 40)) 

    try:
        pygame.display.flip() # Actualizar la pantalla
    except pygame.error as e:
         print(f"Error al actualizar pantalla (pygame.display.flip): {e}")


def main():
    global mapa_cargado, inicio_pos, fin_pos, camino_encontrado, nodos_explorados, tiempo_ejecucion, pantalla, mensaje_estado, filas, columnas, nombre_mapa_actual, largo_camino

    ancho_inicial, alto_inicial = 600, 450
    try:
        pantalla = pygame.display.set_mode((ancho_inicial, alto_inicial), pygame.RESIZABLE)
        pygame.display.set_caption("Lab 27: Comparación de Algoritmos")
    except pygame.error as e:
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
                 if filas > 0: alto_minimo = filas * TAMANO_CELDA + 60 # Más espacio para texto
                 alto_final = max(nuevo_alto, alto_minimo) 
                 ancho_final = max(nuevo_ancho, ancho_inicial if columnas == 0 else columnas * TAMANO_CELDA)
                 try:
                     pantalla = pygame.display.set_mode((ancho_final, alto_final), pygame.RESIZABLE)
                 except pygame.error: pass # Ignorar errores de redimensionamiento temporal

            if evento.type == pygame.KEYDOWN:
                 if evento.key == pygame.K_l: # Tecla L
                    ruta_relativa, nombre_base = pedir_nombre_archivo_terminal()
                    if ruta_relativa:
                        mapa_cargado, inicio_pos, fin_pos = cargar_datos(ruta_relativa)
                        if mapa_cargado and inicio_pos and fin_pos:
                            nombre_mapa_actual = nombre_base
                            filas = len(mapa_cargado)
                            columnas = len(mapa_cargado[0])
                            ancho_pantalla = columnas * TAMANO_CELDA
                            alto_pantalla = filas * TAMANO_CELDA + 60 # Espacio para 2 líneas de texto
                            pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)
                            camino_encontrado = None
                            mensaje_estado = f"Mapa '{nombre_mapa_actual}' cargado. Elige algoritmo (1, 2, 3)."
                        else:
                            mapa_cargado = None; filas = 0; columnas = 0
                            mensaje_estado = "Error al cargar mapa o falta S/E."
                    else:
                         mensaje_estado = "Carga cancelada o archivo no encontrado."
                 
                 # --- Teclas para ejecutar las variantes ---
                 elif evento.key == pygame.K_1: # Tecla 1 para Dijkstra
                    ejecutar_experimento("dijkstra")
                 
                 elif evento.key == pygame.K_2: # Tecla 2 para A*
                    ejecutar_experimento("a_estrella")
                 
                 elif evento.key == pygame.K_3: # Tecla 3 para Greedy
                    ejecutar_experimento("greedy")

        # --- Dibujar ---
        actualizar_pantalla()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()