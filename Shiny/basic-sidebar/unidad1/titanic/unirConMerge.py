titanicPersonales = titanic[["PassengerId", "Age", "Sex", "Pclass"]].copy()
titanicEconomicos = titanic[["PassengerId", "Fare", "Embarked"]].copy()

titanicUnido = pd.merge(titanicPersonales, titanicEconomicos, on="PassengerId")
print(titanicUnido.head(5))

print(titanic.loc[3])

