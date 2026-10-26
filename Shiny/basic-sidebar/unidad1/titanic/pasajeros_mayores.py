pasajeros_mayores = (titanic[["Name", "Pclass", "Age", "Survived"]]
    .sort_values(by="Age", ascending=False)
    .head(5)
)

print(pasajeros_mayores)
