titanic["Es_Menor"]= titanic["Age"] < 18
print(titanic[["Name", "Age", "Es_Menor"]].head(20))
