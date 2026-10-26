texto = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

# 1.- crear un diccionario con la frecuencia de cada carácter, sin espacios
frecuencias = {}
for caracter in texto:
    if caracter != " " and caracter != "\n":
        frecuencias[caracter] = frecuencias.get(caracter, 0) + 1

# 2.- encontrar y mostrar el carácter que más se repite
caracter_mas_repetido = max(frecuencias, key=frecuencias.get)
print(f"Diccionario de frecuencias:\n{frecuencias}\n")
print(f"El carácter más repetido es: '{caracter_mas_repetido}' (se repite {frecuencias[caracter_mas_repetido]} veces)\n")

# 3.- mostrar las palabras que contienen el carácter más repetido y su frecuencia en esa palabra
palabras = texto.replace(",", "").replace(".", "").split()

print(f"Palabras que contienen '{caracter_mas_repetido}':")
for palabra in palabras:
    if caracter_mas_repetido in palabra:
        conteo = palabra.count(caracter_mas_repetido)
        print(f"• {palabra}: {conteo} veces")
