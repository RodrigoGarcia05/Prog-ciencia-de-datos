import matplotlib.pyplot as plt
import numpy as np 

tiempo = np.arange(0,30)
senal= np.random.randint(0, 2, size=30)

print(senal)

plt.figure(figsize=(20,10))
plt.step(tiempo, senal, color="Red")
         
plt.title('CAMBIOS DE ESTADO DE SEÑAL')
plt.xlabel('INSTANTE DE TIEMPO')
plt.ylabel('ESTADO')
plt.grid(True)

plt.show()
