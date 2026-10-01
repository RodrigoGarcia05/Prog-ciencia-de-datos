import numpy as np
from random import random
import matplotlib.cm as cm
import matplotlib.pyplot as plt

dim = 100
num = dim**2
p = 0.25

valores = [1 * (random() < p) for i in range(num)]
actual = np.reshape(valores, (dim, dim))


def mapeo(pos):
    fila = pos // dim
    columna = pos % dim
    return actual[fila, columna]


assert all([mapeo(x) == valores[x] for x in range(num)])


def paso(pos):
    fila = pos // dim
    columna = pos % dim

    vecindad = actual[
        max(0, fila - 1):min(dim, fila + 2),
        max(0, columna - 1):min(dim, columna + 2)
    ]

    return 1 * (np.sum(vecindad) - actual[fila, columna] == 3)


dur = 100

historial_vivos = []

for iteracion in range(dur):

    valores = [paso(x) for x in range(num)]

    vivos = sum(valores)
    historial_vivos.append(vivos)

    print(iteracion, vivos)

    if vivos == 0:
        break

    actual = np.reshape(valores, (dim, dim))

plt.figure(figsize=(20, 10))
plt.plot(historial_vivos)
plt.xlabel("ITERACION")
plt.ylabel("CELULAS VIVAS")
plt.title("EVOLUCION DE LAS CELULAS VIVAS")
plt.grid(True)
plt.show()
