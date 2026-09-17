import matplotlib.pyplot as plt 

plt.figure(figsize= (20,10))
plt.hist(titanic["Age"].dropna(), bins=80, color="skyblue", edgecolor="gray")

plt.title("HISTOGRAMA DE LAS EDADES")
plt.xlabel('EDAD')
plt.ylabel('FRECUENCIA')
plt.show()
