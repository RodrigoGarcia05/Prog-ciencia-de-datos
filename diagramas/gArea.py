import matplotlib.pyplot as plt
import numpy as np

tiempo = np.arange(1, 51)
cambiosAleatorios = np.random.randn(50) 
serieAcumulada = np.cumsum(cambiosAleatorios) 

print(serieAcumulada)

plt.figure(figsize=(20, 10))
plt.fill_between(tiempo, serieAcumulada, color="Red")
plt.plot(tiempo, serieAcumulada, color="Black")

plt.title('SERIE ACUMULATIVA ALEATORIA EN EL TIEMPO')
plt.xlabel('TIEMPO')
plt.ylabel('VALOR ACUMULADO')
plt.grid(True)
plt.show()
