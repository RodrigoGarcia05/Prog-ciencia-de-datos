import matplotlib.pyplot as plt
import numpy as np

categorias = ['Cat A', 'Cat B', 'Cat C', 'Cat D']

medias = np.random.randint(20, 81, size=4)
desviaciones = np.random.randint(3, 12, size=4)

print(f"Medias: {medias}")
print(f"Desviaciones: {desviaciones}")

plt.figure(figsize=(20, 10))
plt.bar(categorias, medias, yerr=desviaciones, capsize=25, color="Red", edgecolor="Black")

plt.title('MEDIAS Y DESVIACIÓN ESTÁNDAR POR CATEGORÍA')
plt.xlabel('CATEGORÍAS')
plt.ylabel('VALOR MEDIO')
plt.grid(True)

plt.show()
