menores= titanic[titanic["Age"]<18]
total_menores=len(menores)
print(total_menores)

menores_por_clase = menores["Pclass"].value_counts()
print (menores_por_clase)

sobrevivientes_por_clase = menores.groupby("Pclass")["Survived"].sum()
print(sobrevivientes_por_clase)
