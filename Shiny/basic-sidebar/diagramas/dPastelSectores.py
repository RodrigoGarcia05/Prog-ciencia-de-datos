import matplotlib.pyplot as plt

conteo = titanic["Survived"].value_counts()

categorias = ["Sobrevivientes", "No sobrevivientes"]
valores = [conteo[1], conteo[0]]

a =['skyblue', 'gray']

plt.figure(figsize=(20, 8))
plt.pie(valores, labels=categorias, autopct="%1.1f%%", startangle=90, colors= a)
plt.title("DIAGRAMA DE SECTORES CON LOS FALLECIDOS Y SUPERVIVIENTES")
plt.show()
