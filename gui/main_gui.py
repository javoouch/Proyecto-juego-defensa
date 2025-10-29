# /gui/main_gui.py
import pygame
import sys
import os
import time 

script_dir = os.path.dirname(__file__) 
project_root = os.path.dirname(script_dir) 
src_path = os.path.join(project_root, 'src') 
if src_path not in sys.path:
    sys.path.append(src_path)


try:
    
    from algoritmo_a_estrella import cargar_datos, resolver_problema, calcular_heuristica
except ImportError as e:
    print(f"Error al importar: {e}")
    print("Asegúrate de que el archivo '/src/algoritmo_a_estrella.py' existe y no tiene errores.")
    sys.exit(1)
except Exception as e:
    print(f"Otro error al importar: {e}") 
    sys.exit(1)


try:
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
        print("--- DEBUG: Pygame font inicializado ---")
except pygame.error as e:
    print(f"Error inicializando Pygame o sus módulos: {e}")
    sys.exit(1)

TAMANO_CELDA = 25
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)     
VERDE = (0, 255, 0)   
AZUL = (0, 0, 255)    
AMARILLO = (255, 255, 0) 
GRIS = (200, 200, 200) 
FUENTE_TAM = 20


mapa_cargado = None
inicio_pos = None
fin_pos = None
camino_encontrado = None
nodos_explorados = 0
tiempo_ejecucion = 0
pantalla = None
mensaje_estado = "Presiona 'L' para cargar mapa (se pedirá en terminal), ESPACIO para ejecutar"
filas, columnas = 0, 0


def pedir_nombre_archivo_terminal():
    """Pide al usuario el nombre del archivo del mapa en la terminal."""
    print("\n--- Cargar Mapa ---")
    ruta_data = os.path.join(project_root, 'data')
    print(f"Archivos disponibles en '{ruta_data}':")
    try:
        archivos_txt = [f for f in os.listdir(ruta_data) if f.endswith('.txt')]
        if not archivos_txt:
            print("  (No se encontraron archivos .txt)")
            return None
        for archivo in archivos_txt:
            print(f"  - {archivo}")
    except FileNotFoundError:
        print(f"  Error: La carpeta '{ruta_data}' no existe.")
        return None
        
    nombre = input("Escribe el nombre del archivo (ej: caso_base.txt): ")
    ruta_relativa = os.path.join('data', nombre) 
    ruta_completa_test = os.path.join(project_root, ruta_relativa)
    if not os.path.exists(ruta_completa_test):
        print(f"Advertencia: El archivo '{nombre}' no parece existir en '{ruta_data}'.")
    return ruta_relativa 


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
    for (fila, columna) in camino[1:-1]: 
         pygame.draw.rect(pantalla, VERDE,
                         (columna * TAMANO_CELDA + 2, fila * TAMANO_CELDA + 2,
                          TAMANO_CELDA - 4, TAMANO_CELDA - 4)) 

def mostrar_texto(pantalla, texto, posicion, color=NEGRO):
    """Muestra texto en la pantalla."""
    if not pantalla: return
    try:
        if not pygame.font.get_init():
             pygame.font.init()
             print("--- DEBUG: Pygame font reinicializado en mostrar_texto ---")
        
        fuente = pygame.font.SysFont(None, FUENTE_TAM) 
        superficie_texto = fuente.render(texto, True, color)
        pantalla.blit(superficie_texto, posicion)
    except pygame.error as e:
        print(f"Error de Pygame al renderizar texto '{texto}': {e}")
    except Exception as e:
        print(f"Error inesperado al mostrar texto '{texto}': {e}")


def main():
    global mapa_cargado, inicio_pos, fin_pos, camino_encontrado, nodos_explorados, tiempo_ejecucion, pantalla, mensaje_estado, filas, columnas

    ancho_inicial, alto_inicial = 600, 450
    try:
        pantalla = pygame.display.set_mode((ancho_inicial, alto_inicial), pygame.RESIZABLE)
        pygame.display.set_caption("Minijuego A* | L: Cargar | ESPACIO: Ejecutar | Click: Test")
        print("--- DEBUG: Pantalla Pygame inicializada ---")
    except pygame.error as e:
        print(f"Error CRÍTICO al inicializar Pygame display: {e}")
        sys.exit(1)

    ejecutando = True
    while ejecutando:
       
        eventos = pygame.event.get() 

        for evento in eventos: 
            if evento.type == pygame.QUIT:
                print("--- DEBUG: Evento QUIT detectado ---")
                ejecutando = False

            elif evento.type == pygame.VIDEORESIZE:
                 print(f"--- DEBUG: Evento VIDEORESIZE detectado: {evento.w}x{evento.h} ---")
                 nuevo_ancho, nuevo_alto = evento.w, evento.h
                 alto_minimo = alto_inicial 
                 if filas > 0: 
                     alto_minimo = filas * TAMANO_CELDA + 50 
                 
                 alto_final = max(nuevo_alto, alto_minimo) 
                 ancho_final = max(nuevo_ancho, ancho_inicial if columnas == 0 else columnas * TAMANO_CELDA)

                 try:
                     pantalla = pygame.display.set_mode((ancho_final, alto_final), pygame.RESIZABLE)
                     print(f"--- DEBUG: Pantalla redimensionada a {ancho_final}x{alto_final} ---")
                 except pygame.error as e:
                      print(f"Error al redimensionar ventana: {e}")

            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                print(f"--- DEBUG: ¡CLICK DEL MOUSE DETECTADO! Pos: {evento.pos} ---")
           

            elif evento.type == pygame.KEYDOWN:
                 print(f"--- DEBUG: Tecla presionada! Código: {evento.key} (L={pygame.K_l}, ESPACIO={pygame.K_SPACE}) ---") 

                 if evento.key == pygame.K_l: 
                    print("--- DEBUG: Tecla L procesando... ---") 
                    ruta_relativa = pedir_nombre_archivo_terminal() 
                    if ruta_relativa:
                        mapa_cargado, inicio_pos, fin_pos = cargar_datos(ruta_relativa) 
                        
                        if mapa_cargado and inicio_pos and fin_pos: 
                            filas = len(mapa_cargado)
                            columnas = len(mapa_cargado[0])
                            ancho_pantalla = columnas * TAMANO_CELDA
                            alto_pantalla = filas * TAMANO_CELDA + 50 
                            try:
                                pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)
                                print(f"--- DEBUG: Pantalla redimensionada para mapa {ancho_pantalla}x{alto_pantalla} ---")
                            except pygame.error as e:
                                print(f"Error al redimensionar para el mapa: {e}")
                            camino_encontrado = None
                            nodos_explorados = 0
                            tiempo_ejecucion = 0
                            mensaje_estado = f"Mapa '{os.path.basename(ruta_relativa)}' cargado. Presiona ESPACIO."
                            print("--- DEBUG: Mapa cargado OK ---")
                        elif mapa_cargado: 
                            mensaje_estado = "Error: Mapa cargado pero falta 'S' o 'E'. Revisa el archivo."
                            print(f"--- DEBUG: Falla - Falta S o E en {ruta_relativa} ---")
                            mapa_cargado = None 
                            filas, columnas = 0,0
                        else: 
                             mensaje_estado = "Error al cargar el archivo del mapa. Revisa terminal."
                             print(f"--- DEBUG: Falla en cargar_datos para {ruta_relativa} ---")
                             mapa_cargado = None 
                             filas, columnas = 0, 0
                    else: 
                         mensaje_estado = "Carga cancelada o archivo no encontrado. Intenta [L] de nuevo."
                         print("--- DEBUG: pedir_nombre_archivo_terminal falló ---")

                 elif evento.key == pygame.K_SPACE: 
                    print("--- DEBUG: Tecla ESPACIO procesando... ---")
                    if mapa_cargado and inicio_pos and fin_pos:
                        mensaje_estado = "Ejecutando A*..."
                        print(mensaje_estado) 
                        if pantalla: 
                            pantalla.fill(BLANCO)
                            dibujar_mapa(pantalla, mapa_cargado)
                            dibujar_grid(pantalla, filas, columnas)
                            mostrar_texto(pantalla, mensaje_estado, (10, filas * TAMANO_CELDA + 10))
                            pygame.display.flip() 
                        
                        start_time = time.time()
                        camino_encontrado, nodos_explorados = resolver_problema(mapa_cargado, inicio_pos, fin_pos)
                        end_time = time.time()
                        tiempo_ejecucion = end_time - start_time

                        if camino_encontrado:
                            mensaje_estado = f"Camino encontrado ({len(camino_encontrado)-1} pasos). Nodos: {nodos_explorados}. T: {tiempo_ejecucion:.4f}s"
                        else:
                            mensaje_estado = f"No se encontró camino. Nodos: {nodos_explorados}. T: {tiempo_ejecucion:.4f}s"
                        print(mensaje_estado) 
                    else:
                        mensaje_estado = "Carga un mapa válido (con S y E) primero usando 'L'."
                        print(mensaje_estado)
                 else:
                     print(f"--- DEBUG: Tecla con código {evento.key} no tiene acción asignada ---")

     
        if pantalla: 
             pantalla.fill(BLANCO)

             if mapa_cargado and filas > 0 and columnas > 0:
                 dibujar_mapa(pantalla, mapa_cargado)
                 dibujar_camino(pantalla, camino_encontrado)
                 dibujar_grid(pantalla, filas, columnas)
                 mostrar_texto(pantalla, mensaje_estado, (10, filas * TAMANO_CELDA + 10))
             else:
                  mostrar_texto(pantalla, "Presiona 'L' (mira la terminal) para cargar un mapa.", (10, 10))
                  mostrar_texto(pantalla, mensaje_estado, (10, 40)) 

             try:
                 pygame.display.flip() 
             except pygame.error as e:
                  print(f"Error al actualizar pantalla (pygame.display.flip): {e}")
                  ejecutando = False 

    
    pygame.quit()
    print("--- DEBUG: Pygame quit ---") 
    sys.exit()

import os 
if __name__ == '__main__':
    main()