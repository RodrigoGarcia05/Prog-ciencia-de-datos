import matplotlib.pyplot as plt

conteoClases = titanic.groupby(["Pclass", "Survived"]).size().unstack()
conteoClases.columns = ["Fallecidos", "Sobrevivientes"]

conteoClases.plot(kind="bar", stacked=True, figsize=(20,10), color=["gray", "skyblue"], edgecolor="black")

plt.title("DIAGRAMA DE BARRAS CON EL NÚMERO DE PERSONAS FALLECIDAS Y SUPERVIVIENTES ACUMULADAS EN CADA CLASE")
plt.xlabel("CLASE")
plt.ylabel("NÚMERO DE PERSONAS")
plt.xticks(rotation =0)

plt.show()
