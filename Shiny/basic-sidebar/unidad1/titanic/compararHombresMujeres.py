titanicHombres = titanic[titanic["Sex"] == "male"].reset_index(drop=True)
titanicMujeres = titanic[titanic["Sex"] == "female"].reset_index(drop=True)

unionSexos = pd.merge(titanicHombres, titanicMujeres, left_index= True, right_index=True, suffixes=("Hombre", "Mujer"))

print(unionSexos.head())
                      
