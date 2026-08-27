

import re

texto_original = input("Ingresa una palabra o frase para verificar si es un palindromo: ")

#convertir a minúsculas y quitar caracteres no alfanuméricos
texto_limpio = re.sub(r'[^a-zA-Z0-9]', '', texto_original).lower()

#invierte  cadena ([::-1])
if texto_limpio and texto_limpio == texto_limpio[::-1]:
    print("Es un palíndromo")
else:
    print("No es un palíndromo.")
