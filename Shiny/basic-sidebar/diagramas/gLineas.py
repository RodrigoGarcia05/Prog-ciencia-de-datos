import numpy as np 
import matplotlib.pyplot as plt

np.random.seed(0)
dias = np.arange(1, 31)
ventas = np.random.randint(50, 200, size= 30)

print(ventas)

plt.figure(figsize=(20,8))
plt.plot(dias, ventas, marker='o', color='tab:Red')
plt.title('VENTAS DIARIAS SIMULADAS')
plt.xlabel('DIA')
plt.ylabel('VENTAS')
plt.grid(True)
plt.show()
