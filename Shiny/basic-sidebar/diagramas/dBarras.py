import matplotlib.pyplot as plt

conteoClases = titanic["Pclass"].value_counts().sort_index()
plt.figure(figsize=(20,10))
conteoClases.plot(kind="bar", color="skyblue", edgecolor="gray")

plt.title("DIAGRAMA DE BARRAS CON EL NÚMERO DE PERSONAS EN CADA CLASE")
plt.xlabel("Clase")
plt.ylabel("NÚMERO DE PERSONAS")
plt.xticks(rotation=0)
plt.show()
