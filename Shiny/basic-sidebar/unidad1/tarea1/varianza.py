import numpy as np

N = int(input("Ingresa el tamaño del vector: "))

vector = np.random.random(N)

print("\nVector:")
print(vector)

media = np.mean(vector)

varianza = np.mean((vector - media) ** 2)

print("\nLa media es:", media)
print("La varianza es:", varianza)
