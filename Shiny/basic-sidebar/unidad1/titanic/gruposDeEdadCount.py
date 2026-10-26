grupos = [-1, 12, 25, 60, 100]
etiquetas = ["Niños (0-12)", "Jovenes(13-25)", "Adultos(26-60)", "Mayores(61+)"]
titanic["Grupo_edad"] = pd.cut(titanic["Age"], grupos, etiquetas)

sobrevivientesGrupo = titanic.groupby("Grupo_edad",observed= False)["Survived"].agg(
    sobrevivieron="sum",
    totalPasajeros="count"
)
print(sobrevivientesGrupo)
