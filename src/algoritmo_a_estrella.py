# /src/algoritmo_a_estrella.py
import time
import heapq 
import os # Necesario para cargar datos

def cargar_datos(nombre_archivo_relativo):
    """
    Carga un mapa desde una ruta relativa a la raíz del proyecto (ej: "data/caso_base.txt").
    Retorna el mapa como una lista de listas, y las posiciones de inicio y fin.
    """
    mapa = []
    inicio = None
    fin = None
    try:
        # Construye la ruta absoluta basada en la ubicación de este script
        script_dir = os.path.dirname(__file__) # Directorio actual (src)
        project_root = os.path.dirname(script_dir) # Raíz del proyecto
        ruta_completa = os.path.join(project_root, nombre_archivo_relativo)

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
        print(f"Mapa '{nombre_archivo_relativo}' cargado correctamente.")
        if inicio is None or fin is None:
             print("Advertencia: No se encontró 'S' (inicio) o 'E' (fin) en el mapa.")
        return mapa, inicio, fin
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de mapa en '{ruta_completa}'")
        return None, None, None
    except Exception as e:
        print(f"Error al cargar el mapa: {e}")
        return None, None, None

def calcular_heuristica_manhattan(a, b):
    """Calcula la distancia Manhattan entre dos puntos (tuplas)."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def buscar_camino(mapa, inicio, fin, estrategia="a_estrella"):
    """
    Implementa A*, Dijkstra y Greedy Best-First.
    Retorna (camino, nodos_explorados, largo_camino).
    'largo_camino' es -1 si no se encuentra.
    """
    if not mapa or not inicio or not fin:
        print("Error: Mapa, inicio o fin inválidos para resolver.")
        return None, 0, -1

    lista_abierta = []
    contador = 0
    # Calcular heurística inicial
    h_inicial = calcular_heuristica_manhattan(inicio, fin)
    
    # La prioridad inicial depende de la estrategia
    if estrategia == "dijkstra":
        prioridad_inicial = 0 # g(n)
    elif estrategia == "greedy":
        prioridad_inicial = h_inicial # h(n)
    else: # "a_estrella" por defecto
        prioridad_inicial = 0 + h_inicial # g(n) + h(n)

    heapq.heappush(lista_abierta, (prioridad_inicial, contador, inicio)) 
    
    g_cost = {inicio: 0}
    # f_cost ya no se guarda, solo se usa para la prioridad del heap
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
            largo_camino = len(camino) - 1 # El largo real del camino (costo)
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
                        
                        # --- AQUÍ ESTÁ LA MAGIA ---
                        # La prioridad cambia según la estrategia
                        prioridad = 0
                        if estrategia == "a_estrella":
                            prioridad = tentativo_g_cost + heuristica
                        elif estrategia == "dijkstra":
                            prioridad = tentativo_g_cost
                        elif estrategia == "greedy":
                            prioridad = heuristica
                        
                        contador += 1
                        heapq.heappush(lista_abierta, (prioridad, contador, vecino_pos))

    print(f"No se encontró un camino para la estrategia '{estrategia}'.")
    return None, nodos_explorados, -1