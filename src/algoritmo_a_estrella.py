# /src/algoritmo_a_estrella.py
import time
import heapq # Ideal para la lista abierta (cola de prioridad)

def cargar_datos(nombre_archivo):
    """
    Carga un mapa desde un archivo .txt en la carpeta /data.
    Retorna el mapa como una lista de listas, y las posiciones de inicio y fin.
    """
    mapa = []
    inicio = None
    fin = None
    try:
        # Ajusta la ruta para que funcione desde donde se llame (ej. desde gui/)
        # Asume que data/ está al mismo nivel que src/ y gui/
        script_dir = os.path.dirname(__file__) # Directorio actual (src)
        project_root = os.path.dirname(script_dir) # Raíz del proyecto
        ruta_completa = os.path.join(project_root, nombre_archivo) # nombre_archivo debe ser relativo a la raíz, ej "data/caso_base.txt"

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
        return None, None, None # Devuelve None si hay error
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
    # El heap guarda tuplas: (f_cost, posicion)
    # Agregamos un contador para desempatar nodos con el mismo f_cost
    contador = 0 
    heapq.heappush(lista_abierta, (calcular_heuristica(inicio, fin), contador, inicio)) 
    
    # Diccionarios para guardar los costos y el camino
    g_cost = {inicio: 0}
    f_cost = {inicio: calcular_heuristica(inicio, fin)}
    padres = {inicio: None}
    
    # Usaremos un set para la lista cerrada para búsquedas rápidas O(1)
    lista_cerrada = set() 
    
    nodos_explorados = 0

    while lista_abierta:
        # 1. Obtener el nodo con el menor f_cost de la lista abierta
        _, _, actual = heapq.heappop(lista_abierta)
        
        # Si ya exploramos este nodo (puede estar duplicado en el heap), lo ignoramos
        if actual in lista_cerrada:
            continue
            
        nodos_explorados += 1 # Contamos solo cuando lo procesamos por primera vez
            
        # 2. Si llegamos al final, reconstruir el camino
        if actual == fin:
            camino = []
            temp = actual
            while temp:
                camino.append(temp)
                temp = padres[temp]
            return camino[::-1], nodos_explorados # Retornar camino invertido

        # 3. Mover a la lista cerrada
        lista_cerrada.add(actual)

        # 4. Explorar vecinos (arriba, abajo, izquierda, derecha)
        vecinos_mov = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Derecha, Izquierda, Abajo, Arriba
        for move_x, move_y in vecinos_mov:
            vecino_pos = (actual[0] + move_x, actual[1] + move_y)

            # Validar si el vecino está dentro del mapa
            if 0 <= vecino_pos[0] < len(mapa) and 0 <= vecino_pos[1] < len(mapa[0]):
                # Validar si no es un obstáculo ('X') y no está en la lista cerrada
                 if mapa[vecino_pos[0]][vecino_pos[1]] != 'X' and vecino_pos not in lista_cerrada:
                    
                    tentativo_g_cost = g_cost[actual] + 1 # Costo de moverse a un vecino es 1

                    # Si encontramos un camino mejor o es la primera vez que vemos este vecino
                    if vecino_pos not in g_cost or tentativo_g_cost < g_cost[vecino_pos]:
                        padres[vecino_pos] = actual
                        g_cost[vecino_pos] = tentativo_g_cost
                        heuristica = calcular_heuristica(vecino_pos, fin)
                        f_cost[vecino_pos] = tentativo_g_cost + heuristica
                        # Añadir a la lista abierta (o actualizar si ya estaba con mayor costo)
                        contador += 1
                        heapq.heappush(lista_abierta, (f_cost[vecino_pos], contador, vecino_pos))

    print("No se encontró un camino.")
    return None, nodos_explorados # Si no se encuentra camino

# Importar 'os' al principio del archivo si no está ya
import os