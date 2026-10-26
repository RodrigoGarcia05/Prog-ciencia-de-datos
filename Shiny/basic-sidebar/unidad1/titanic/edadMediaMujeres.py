edad_media_mujeres = titanic[titanic["Sex"] == "female"].groupby("Pclass")["Age"].mean()

print(edad_media_mujeres)
