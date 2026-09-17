import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(100)
grupo1 = np.random.normal(0.0, 40.0, size= 100)
grupo2 = np.random.normal(10.0, 50.0, size= 100)
grupo3 = np.random.normal(-30.0, 100.0, size= 100)

datos = pd.DataFrame({"Grupo 1": grupo1, "Grupo 2": grupo2, "Grupo 3": grupo3})

print(grupo1)
print(grupo2)
print(grupo3)

plt.figure(figsize=(20,10))
plt.boxplot(datos, tick_labels=datos.columns)
plt.title('GRUPOS DE 100 DATOS CON DISTRIBUCIONES NORMALES DIFERENTES')
plt.ylabel('VALORES')
plt.grid(True)
plt.show()

