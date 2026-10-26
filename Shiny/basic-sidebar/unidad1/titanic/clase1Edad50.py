condicion = ((titanic["Pclass"]== 1) & (titanic["Survived"]== 1) & (titanic["Age"]>= 50))
pasajeros1clase50 = titanic[condicion]

print(f"Pasajeros encontrados: {len(pasajeros1clase50)}")
print(pasajeros1clase50[["Name", "Age", "Pclass", "Survived"]])
