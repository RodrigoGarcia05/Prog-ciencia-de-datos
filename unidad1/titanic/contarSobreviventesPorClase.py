sobrevivientesClaseSexo = titanic.groupby(["Pclass", "Sex"])["Survived"].value_counts()
print(sobrevivientesClaseSexo)
