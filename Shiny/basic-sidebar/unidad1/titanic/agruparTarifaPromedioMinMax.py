tarifasEmbarcacion= (
titanic.groupby("Embarked")["Fare"]
.agg(Promedio= "mean", Minimo= "min", Maximo= "max").round(1)
)
print(tarifasEmbarcacion)
