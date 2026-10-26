import numpy as np

filas = int(input("Ingresa el número de filas: "))
columnas = int(input("Ingresa el número de columnas: "))

matriz = np.random.random((filas, columnas))

print("\nMatriz:")
print(matriz)

media = np.mean(matriz)

print("\nLa media de la matriz es:", media)
