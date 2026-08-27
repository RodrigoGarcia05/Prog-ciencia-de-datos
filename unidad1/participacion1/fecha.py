

from datetime import datetime

def es_primo(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def clasificar_numero(n):
    propiedades = []
    # par o impar
    if n % 2 == 0:
        propiedades.append("par")
    else:
        propiedades.append("impar")
    
    # primo
    if es_primo(n):
        propiedades.append("primo")
        
    return " y ".join(propiedades)

def es_bisiesto(anio):
    # Un año es bisiesto si es divisible por 4, 
    # excepto si es divisible por 100, a menos que también sea por 400.
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

# pedir la fecha al usuario
entrada = input("Ingresa una fecha (formato DD/MM/AAAA): ")

try:
    # validar la fecha
    fecha = datetime.strptime(entrada, "%d/%m/%Y")
    dia = fecha.day
    mes = fecha.month
    anio = fecha.year

    # evaluar día y mes
    print(f"\n--- Análisis de la fecha: {entrada} ---")
    print(f"• Día ({dia}): Es {clasificar_numero(dia)}.")
    print(f"• Mes ({mes}): Es {clasificar_numero(mes)}.")

    # evaluar si el año es bisiesto
    if es_bisiesto(anio):
        print(f"• Año ({anio}): Es bisiesto.")
    else:
        print(f"• Año ({anio}): NO es bisiesto.")

except ValueError:
    print("Ingresa una fecha válida en el formato DD/MM/AAAA.")

