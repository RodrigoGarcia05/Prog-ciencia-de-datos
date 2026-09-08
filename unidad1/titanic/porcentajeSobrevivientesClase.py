titanic_edad = titanic.dropna(subset=["Age"]).copy()

titanic_edad["Grupo_Edad"] = "Mayor"
titanic_edad.loc[titanic_edad["Age"] < 18, "Grupo_Edad"] = "Menor"

porcentaje = (
    titanic_edad.groupby(["Pclass", "Grupo_Edad"])["Survived"].mean() * 100
)

print(porcentaje)
