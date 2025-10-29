# /src/algoritmo_a_estrella.py
import time
import heapq 
def cargar_datos(nombre_archivo):
    mapa = []
    inicio = None
    fin = None
    try:
        script_dir = os.path.dirname(__file__) 
        project_root = os.path.dirname(script_dir) 
        ruta_completa = os.path.join(project_root, nombre_archivo) # nombre_archivo debe ser ej "data/caso_base.txt"

        with open(ruta_completa, 'r') as f:
            for i, linea in enumerate(f):
                fila = []
                for j, char in enumerate(linea.strip()):
                    if char == 'S':
                        inicio = (i, j)
                    elif char == 'E':
                        fin = (i, j)
                    fila.append(char)
                mapa.append(fila)
        print(f"Mapa '{nombre_archivo}' cargado correctamente.")
        if inicio is None or fin is None:
             print("Advertencia: No se encontró 'S' (inicio) o 'E' (fin) en el mapa.")
        return mapa, inicio, fin
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de mapa en '{ruta_completa}'")
        return None, None, None 
    except Exception as e:
        print(f"Error al cargar el mapa: {e}")
        return None, None, None

def calcular_heuristica(a, b):
    """Calcula la distancia Manhattan entre dos puntos (tuplas)."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def resolver_problema(mapa, inicio, fin):
    """
    Implementa el algoritmo A* para encontrar el camino más corto.
    Retorna una tupla: (camino, nodos_explorados).
    'camino' es una lista de tuplas (posiciones) o None si no se encuentra.
    'nodos_explorados' es el contador de nodos sacados de la lista abierta.
    """
    if not mapa or not inicio or not fin:
        print("Error: Mapa, inicio o fin inválidos para resolver.")
        return None, 0

    lista_abierta = []
    contador = 0 
    heapq.heappush(lista_abierta, (calcular_heuristica(inicio, fin), contador, inicio)) 
    
   
    g_cost = {inicio: 0}
    f_cost = {inicio: calcular_heuristica(inicio, fin)}
    padres = {inicio: None}
    
   
    lista_cerrada = set() 
    
    nodos_explorados = 0

    while lista_abierta:
       
        _, _, actual = heapq.heappop(lista_abierta)
        
        
        if actual in lista_cerrada:
            continue
            
        nodos_explorados += 1 
            
        if actual == fin:
            camino = []
            temp = actual
            while temp:
                camino.append(temp)
                temp = padres[temp]
            return camino[::-1], nodos_explorados 

        lista_cerrada.add(actual)

        vecinos_mov = [(0, 1), (0, -1), (1, 0), (-1, 0)] 
        for move_x, move_y in vecinos_mov:
            vecino_pos = (actual[0] + move_x, actual[1] + move_y)

            if 0 <= vecino_pos[0] < len(mapa) and 0 <= vecino_pos[1] < len(mapa[0]):
                 if mapa[vecino_pos[0]][vecino_pos[1]] != 'X' and vecino_pos not in lista_cerrada:
                    
                    tentativo_g_cost = g_cost[actual] + 1 

                    if vecino_pos not in g_cost or tentativo_g_cost < g_cost[vecino_pos]:
                        padres[vecino_pos] = actual
                        g_cost[vecino_pos] = tentativo_g_cost
                        heuristica = calcular_heuristica(vecino_pos, fin)
                        f_cost[vecino_pos] = tentativo_g_cost + heuristica
                        contador += 1
                        heapq.heappush(lista_abierta, (f_cost[vecino_pos], contador, vecino_pos))

    print("No se encontró un camino.")
    return None, nodos_explorados 

import os