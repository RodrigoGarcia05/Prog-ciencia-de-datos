claseEmbarque = titanic.groupby(["Pclass", "Embarked"]).agg(
    totalPasajeros=("PassengerId", "count"),
    tarifaMaxima= ("Fare", "max"),
)

print(claseEmbarque)

