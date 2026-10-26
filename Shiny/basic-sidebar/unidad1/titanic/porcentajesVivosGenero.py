print(titanic['Survived'].value_counts()/titanic['Survived'].count() *100)
conteo_sexo = titanic["Sex"].value_counts()
print(conteo_sexo)
