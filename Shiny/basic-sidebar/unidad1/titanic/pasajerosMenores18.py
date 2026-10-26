menores= titanic[titanic["Age"]<18]
total_menores=len(menores)
print(f"Total de menores: {total_menores}")

menores_por_clase = menores["Pclass"].value_counts()
print (f"Por clase: {menores_por_clase}")

sobrevivientes_por_clase = menores.groupby("Pclass")["Survived"].sum()
print(f"Sobrevivientes: {sobrevivientes_por_clase}")
