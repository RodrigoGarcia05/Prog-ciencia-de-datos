import numpy as np

# Pedir el tamaño del vector
N = int(input("Ingresa el tamaño del vector: "))

# Generar números aleatorios
vector = np.round(np.random.random(N), 1)

print("\nVector:")
print(vector)

# Obtener valores y sus frecuencias
valores, frecuencias = np.unique(vector, return_counts=True)

# Encontrar la mayor frecuencia
frecuencia_maxima = np.max(frecuencias)

# Obtener la moda
modas = valores[frecuencias == frecuencia_maxima]

print("\nLa moda es:", modas)
print("Frecuencia:", frecuencia_maxima)
