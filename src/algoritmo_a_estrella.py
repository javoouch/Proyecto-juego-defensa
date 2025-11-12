# /src/algoritmo_a_estrella.py
import time
import heapq 
import os
import logging # Importar logging

# Configurar el logger
# (Se configura en main_gui.py, pero podemos obtener el logger aquí)
log = logging.getLogger(__name__)

def cargar_datos(nombre_archivo_relativo):
    """
    Carga un mapa desde una ruta relativa a la raíz del proyecto (ej: "data/caso_base.txt").
    Valida la existencia, formato, y presencia de S/E. [cite: 328, 330]
    """
    mapa = []
    inicio = None
    fin = None
    
    try:
        script_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(script_dir)
        ruta_completa = os.path.join(project_root, nombre_archivo_relativo)

        if not os.path.exists(ruta_completa): # [cite: 328]
            log.error(f"Archivo no encontrado en: {ruta_completa}")
            raise FileNotFoundError(f"No se encontró el archivo en {ruta_completa}")

        with open(ruta_completa, 'r') as f:
            lineas = f.readlines()
            if not lineas: # [cite: 331]
                log.warning(f"El archivo '{nombre_archivo_relativo}' está vacío.")
                return None, None, None, "Error: El archivo está vacío."

            ancho_esperado = len(lineas[0].strip()) # Longitud de la primera fila 

            for i, linea in enumerate(lineas):
                linea_limpia = linea.strip()
                
                # Validar formato de filas y columnas consistentes 
                if len(linea_limpia) != ancho_esperado:
                    log.error(f"Formato inválido: Fila {i} tiene {len(linea_limpia)} columnas, se esperaban {ancho_esperado}.")
                    return None, None, None, "Error: El mapa tiene filas de distinto largo."

                fila = []
                for j, char in enumerate(linea_limpia):
                    if char == 'S':
                        inicio = (i, j)
                    elif char == 'E':
                        fin = (i, j)
                    fila.append(char)
                mapa.append(fila)
        
        if inicio is None or fin is None: # [cite: 331]
             log.warning(f"No se encontró 'S' (inicio) o 'E' (fin) en el mapa '{nombre_archivo_relativo}'.")
             return mapa, None, None, "Error: Mapa no tiene 'S' o 'E'."
        
        log.info(f"Mapa '{nombre_archivo_relativo}' cargado correctamente.")
        return mapa, inicio, fin, "Mapa cargado. Listo para ejecutar."
        
    except FileNotFoundError:
        return None, None, None, "Error: Archivo no encontrado."
    except Exception as e:
        log.error(f"Error inesperado al cargar el mapa: {e}")
        return None, None, None, "Error: Ocurrió un problema al leer el archivo."

def calcular_heuristica_manhattan(a, b):
    """Calcula la distancia Manhattan entre dos puntos (tuplas)."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def buscar_camino(mapa, inicio, fin, estrategia="a_estrella"):
    """
    Implementa A*, Dijkstra y Greedy Best-First.
    Retorna (camino, nodos_explorados, largo_camino).
    """
    if not mapa or not inicio or not fin:
        log.error("Se intentó buscar camino sin mapa, inicio o fin válidos.")
        return None, 0, -1

    log.info(f"Iniciando búsqueda con estrategia: {estrategia.upper()}")
    
    lista_abierta = []
    contador = 0
    h_inicial = calcular_heuristica_manhattan(inicio, fin)
    
    if estrategia == "dijkstra":
        prioridad_inicial = 0
    elif estrategia == "greedy":
        prioridad_inicial = h_inicial
    else: 
        prioridad_inicial = 0 + h_inicial

    heapq.heappush(lista_abierta, (prioridad_inicial, contador, inicio)) 
    
    g_cost = {inicio: 0}
    padres = {inicio: None}
    lista_cerrada = set()
    nodos_explorados = 0

    while lista_abierta:
        prioridad_actual, _, actual = heapq.heappop(lista_abierta)
        
        if actual in lista_cerrada:
            continue
            
        nodos_explorados += 1 
        lista_cerrada.add(actual)

        if actual == fin:
            camino = []
            temp = actual
            while temp:
                camino.append(temp)
                temp = padres[temp]
            largo_camino = len(camino) - 1
            log.info(f"Búsqueda exitosa. Estrategia: {estrategia.upper()}. Pasos: {largo_camino}. Nodos explorados: {nodos_explorados}.") # [cite: 350, 351, 369]
            return camino[::-1], nodos_explorados, largo_camino

        vecinos_mov = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for move_x, move_y in vecinos_mov:
            vecino_pos = (actual[0] + move_x, actual[1] + move_y)

            if 0 <= vecino_pos[0] < len(mapa) and 0 <= vecino_pos[1] < len(mapa[0]):
                 if mapa[vecino_pos[0]][vecino_pos[1]] != 'X' and vecino_pos not in lista_cerrada:
                    
                    tentativo_g_cost = g_cost[actual] + 1

                    if vecino_pos not in g_cost or tentativo_g_cost < g_cost[vecino_pos]:
                        padres[vecino_pos] = actual
                        g_cost[vecino_pos] = tentativo_g_cost
                        
                        heuristica = calcular_heuristica_manhattan(vecino_pos, fin)
                        
                        prioridad = 0
                        if estrategia == "a_estrella":
                            prioridad = tentativo_g_cost + heuristica
                        elif estrategia == "dijkstra":
                            prioridad = tentativo_g_cost
                        elif estrategia == "greedy":
                            prioridad = heuristica
                        
                        contador += 1
                        heapq.heappush(lista_abierta, (prioridad, contador, vecino_pos))

    log.warning(f"No se encontró un camino para la estrategia '{estrategia}'. Nodos explorados: {nodos_explorados}.") # [cite: 341]
    return None, nodos_explorados, -1