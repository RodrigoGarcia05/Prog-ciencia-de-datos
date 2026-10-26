

def dfs(nodo, matriz, visitados):
    """Recorrido en profundidad (DFS) para verificar conectividad."""
    #marca nodo actual como visitado
    visitados[nodo] = True
    # calcula el numero de nodos contando el numero de filas de la matríz
    n = len(matriz)
    for v in range(n):
        # 1. el nodo v no ha sido visitado previamente?
        # 2. Existe una relación directa entre el nodo actual y el nodo v? 1 o true 
        if matriz[nodo][v] and not visitados[v]:
            # si se cumple, nodo pasa a ser v y visita a sus vecinos
            dfs(v, matriz, visitados)

def es_conexo(matriz):
    """Verifica si todos los nodos que tienen conexiónes formen una estructura unida."""
    n = len(matriz)
    # todos los nodos pasan a ser false
    visitados = [False] * n
    
    # encontrar el primer nodo que tenga al menos una conexión
    primer_nodo = -1
    # bucle para recorrer cada fila i de la matriz
    for i in range(n):
        # si la suma es mayor a 0, significa que el nodo i tiene al menos una conexión 
        if sum(matriz[i]) > 0:
            # guarda la posición del nodo que encontramos con conexiónes 
            primer_nodo = i
            #rompe el bucle for, solo ocupamos uno un nodo para empezar 
            break
            
    # si no hay aristas en el grafo, técnicamente tiene un circuito euleriano nulo, esta vacio
    if primer_nodo == -1:
        return True
        
    # hacer DFS desde el primer nodo con conexiones
    dfs(primer_nodo, matriz, visitados)
    
    # comprobar si algún nodo con conexiones quedó sin visitar
    for i in range(n):
        # verifica si el nodo 1 tiene conexiónes y no fue alcanzado por la exploración 
        if sum(matriz[i]) > 0 and not visitados[i]:
            return False
            #si esto ocurre, el grafo esta fragmentado
            
    return True

def analizar_euleriano(matriz):
    #analiza la matriz entera
    """Evalúa la matriz booleana y determina la existencia de camino o circuito."""
    # validación previa de conectividad
    if not es_conexo(matriz):
        return "El grafo no es conexo (los nodos con aristas no están unidos), por lo que no tiene camino ni circuito euleriano."

    # contar los grados impares de cada nodo
    grados_impares = 0
    for fila in matriz:
        # el grado de un nodo es la suma de True/1s en su fila
        grado = sum(fila)
        # suma todos los 1s para obtener el total de las conexiones 
        if grado % 2 != 0:
            # si el resto no es 0, es impar
            grados_impares += 1

    # clasificación euleriana
    if grados_impares == 0:
        return "La matriz TIENE un CIRCUITO EULERIANO, y por tanto también un camino euleriano."
    elif grados_impares == 2:
        return "La matriz TIENE un CAMINO EULERIANO, pero no un circuito euleriano."
    else:
        return f"La matriz NO tiene camino ni circuito euleriano (tiene {grados_impares} vértices de grado impar)."


"CONDICIONES"
"1.- Si todos los nodos son par, es circuito y camino"
"2.- Si solo hay 2 nodos impares, es camino"

#ejemplos

# Matriz 1: Grafo con circuito euleriano (Todos los grados son pares)
matriz_circuito = [
    [0, 1, 1, 0],
    [1, 0, 1, 0],
    [1, 1, 0, 0],
    [0, 0, 0, 0]
]

# Matriz 2: grafo con camino euleriano (Exactamente 2 nodos de grado impar)
matriz_camino = [
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
] 
# triángulo simple (nodos 0, 1 y 2 tienen grado 2 -> circuito)

matriz_ejemplo = [
    [0, 1, 1, 0],
    [1, 0, 1, 1],
    [1, 1, 0, 0],
    [0, 1, 0, 0]
] 

# grados: Nodo 0: 2 (par), Nodo 1: 3 (impar), Nodo 2: 2 (par), Nodo 3: 1 (impar)
# tiene 2 nodos impares -> camino euleriano

matriz_fragmentada = [
    # A (Nodos 0 y 1 conectados entre sí)
    [0, 1, 0, 0],  # Nodo 0: conectado solo al 1
    [1, 0, 0, 0],  # Nodo 1: conectado solo al 0
    
    # B (Nodos 2 y 3 conectados entre sí)
    [0, 0, 0, 1],  # Nodo 2: conectado solo al 3
    [0, 0, 1, 0]   # Nodo 3: conectado solo al 2
]


print("Resultado del análisis:")
print(analizar_euleriano(matriz_ejemplo))
