condicionSouthampton= ((titanic["Sex"]== "female") & (titanic["Pclass"]== 3) & (titanic["Survived"] == 0) & (titanic["Embarked"] == "S"))
mujeresSouthampton = titanic[condicionSouthampton].count()

cantidad = len(mujeresSouthampton)
edad_promedio = mujeresSouthampton["Age"].mean()

print(f"Cantidad de mujeres {cantidad}")
print(f"Edad promedio: {edad_promedio} años")


