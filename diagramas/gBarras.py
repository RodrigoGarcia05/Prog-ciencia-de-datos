import matplotlib.pyplot as plt 
import numpy as np

categorias = ['Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5']
valores = np.random.randint(10, 101, size=5)

print(valores)

fig, ax = plt.subplots(figsize=(20, 10))
plt.bar(categorias, valores, color='red', edgecolor='black')

plt.title('VALORES ALEATORIOS POR CATEGORÍA')
plt.xlabel('CATEGORÍAS')
plt.ylabel('VALORES')
plt.grid(True)
plt.show()
