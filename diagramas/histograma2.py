import matplotlib.pyplot as plt
import numpy as np

numerosdn = np.random.normal(50, 15, size= 1000)
plt.figure(figsize=(20,10))
plt.hist(numerosdn, bins=20, color="Red", edgecolor="Black")

print(numerosdn)

plt.title('DISTRIBUCIÓN NORMAL CON MEDIA 50 Y DESVIACIÓN 15')
plt.xlabel('VALORES')
plt.ylabel('FRECUENCIA')
plt.grid(True)

plt.show()
