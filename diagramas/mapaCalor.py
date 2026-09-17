import matplotlib.pyplot as plt 
import numpy as np 

matriz= np.random.rand(5, 8)

print(matriz)

plt.figure(figsize=(20,10))
plt.imshow(matriz, cmap="hot")

plt.colorbar(label="INTENSIDAD DEL VALOR")

plt.title("MAPA DE CALOR")
plt.xlabel("COLUMNAS")
plt.ylabel("FILAS")

plt.show
