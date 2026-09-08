supervivencia_clase = titanic.groupby("Pclass")["Survived"].mean()*100
print(supervivencia_clase)
