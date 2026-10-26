sobrevivientesOrdenados= (
titanic[titanic["Survived"] == 1][["Sex", "Pclass", "Age", "Survived"]]
.sort_values(by="Age", ascending= True).head(5)
)
print(sobrevivientesOrdenados)
