import matplotlib.pyplot as plt
import numpy as np 

valoresDiscretos = np.random.randint(-10, 10, size=20)

plt.figure(figsize=(20, 10))
plt.stem(valoresDiscretos)

print(valoresDiscretos)

plt.title('GRÁFICO DE TALLO')
plt.xlabel('ÍNDICE DEL DATO')
plt.ylabel('VALOR DISCRETO')
plt.show()
