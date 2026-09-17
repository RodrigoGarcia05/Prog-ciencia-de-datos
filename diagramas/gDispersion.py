import matplotlib.pyplot as plt 
import numpy as np 

horasEstudio = np.random.uniform(0, 10, size=100)
pendiente = 6.0
interseccion = 30.0
ruido = np.random.normal(loc=0, scale=8.0, size=100)
calificaciones = np.clip((pendiente * horasEstudio) + interseccion + ruido, 0, 100)

print(calificaciones)

fig, ax = plt.subplots(figsize=(20, 10))
plt.scatter(x=horasEstudio, y=calificaciones, color='red', edgecolor='Black')

plt.title('SIMULACIÓN: HORAS ESTUDIO VS CALIFICACIONES')
plt.xlabel('HORAS DE ESTUDIO')
plt.ylabel('CALIFICACIÓN')
plt.grid(True)
plt.show()
