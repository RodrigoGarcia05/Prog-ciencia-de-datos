max_edad = titanic["Age"].max()
max_edad_sexo = titanic.groupby("Sex")["Age"].max()
min_edad_sexo = titanic.groupby("Sex")["Age"].min()
posicion_max = titanic["Age"].idxmax()
datos_pasajero_mayor = titanic.loc[posicion_max]

print(max_edad)
print(max_edad_sexo)
print(min_edad_sexo)
print(posicion_max)
print(datos_pasajero_mayor)
