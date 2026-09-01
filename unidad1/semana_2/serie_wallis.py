import math 
pi = math.pi
print (pi)

producto = 1.0
iteraciones = 0

while True:
    iteraciones += 1
    if iteraciones % 2 != 0:
        termino = (iteraciones + 1) / (iteraciones + 2)
    else: 
        termino = (iteraciones + 2) / (iteraciones + 1)

    producto *= termino
    pi_calculado = 4 * producto

    error = abs(pi - pi_calculado)
    if error < 0.001:
        break

print (f" Pi calculado: {pi_calculado:.5f}")
print (f" Pi real: {pi:.5f}")
print (f" Erorr final: {error:.5f}")
print (f" Iteraciones necesarias: {iteraciones}")
