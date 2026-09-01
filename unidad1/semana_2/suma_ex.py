import math 

x = float(input("Ingresa el valor de x: "))

suma = 0.0

print (f"Resultados acumulados para e elevada a {x}")
for n in range (1, 101):
    termino = (x ** n) / math.factorial(n)
    suma += termino
    print(f"n = {n: } | suma = {suma}")
