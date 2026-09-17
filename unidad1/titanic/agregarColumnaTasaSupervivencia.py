tasaClase = titanic.groupby("Pclass")["Survived"].mean().reset_index()
tasaClase.columns = ["Pclass", "TasaSupervivencia"]

dfUnido = pd.merge(titanic, tasaClase, on="Pclass")

print(dfUnido[["PassengerId", "Pclass", "TasaSupervivencia"]].head(10))
