resumenPuertos = (
titanic.groupby("Embarked").agg(
totalPasajeros=("Survived", "count"),
sobrevivientes=("Survived", "sum"),
tasaSupervivencia=("Survived", "mean"),
)
.sort_values(by="tasaSupervivencia", ascending = False)
)

resumenPuertos["tasaSupervivencia"] = resumenPuertos["tasaSupervivencia"].round(3)
print(resumenPuertos)

puertoMax = resumenPuertos["tasaSupervivencia"].idxmax()
print(f"El puerto con mayor tasa de supervivencia fue: {puertoMax}")
