resumenSexo = titanic.groupby("Sex").agg(
    total=("PassengerId", "count"),
    edadPromedio=("Age", "mean"),
    tarifaPromedio=("Fare", "mean"),
    tasaSupervivencia=("Survived", "mean")
).round(2)

print(resumenSexo)
