import math

def resolver_ecuacion_cuadratica(a, b, c):
    # validar que 'a' no sea cero 
    if a == 0:
        return "El coeficiente 'a' no puede ser cero."

    # calcular el discriminante (b^2 - 4ac)
    discriminante = b**2 - 4 * a * c

    # validar que las soluciones sean reales
    if discriminante < 0:
        return "La ecuación no tiene soluciones reales (las raíces son imaginarias)."

    # Calcular las dos soluciones reales
    x1 = (-b + math.sqrt(discriminante)) / (2 * a)
    x2 = (-b - math.sqrt(discriminante)) / (2 * a)

    return x1, x2

#programa
try:
    print("Ingrese los coeficientes: ")
    a = float(input("Ingrese a: "))
    b = float(input("Ingrese b: "))
    c = float(input("Ingrese c: "))

    resultado = resolver_ecuacion_cuadratica(a, b, c)

    if isinstance(resultado, tuple):
        x1, x2 = resultado
        print(f"\nLas soluciones reales son:")
        print(f"x1 = {x1}")
        print(f"x2 = {x2}")
    else:
        print(f"\n{resultado}")

except ValueError:
    print("Error: Por favor ingrese solo números válidos.")
