# tabla de conversión 
hex_a_bin = {
    '0': '0000', '1': '0001', '2': '0010', '3': '0011',
    '4': '0100', '5': '0101', '6': '0110', '7': '0111',
    '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
    'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
}

# pasar de Hexadecimal a Binario
def hex_a_binario(hex_str):
    binario = ""
    for caracter in hex_str.upper():
        binario += hex_a_bin[caracter]
    return binario

# pasar de Binario a Decimal (utiliza base 2)
def binario_a_decimal(bin_str):
    return int(bin_str, 2)

#programa

#datos a analizar 
datos_hex = ["AA55", "1A", "FF", "05", "4C", "5E"]

decimales = []

print("--- Conversión ---")
for hex_num in datos_hex:
    bin_num = hex_a_binario(hex_num)
    dec_num = binario_a_decimal(bin_num)
    decimales.append(dec_num)
    print(f"Hex: {hex_num} -> Binario: {bin_num} -> Decimal: {dec_num}")

# Obtener Máximo y Mínimo
maximo = max(decimales)
minimo = min(decimales)

print("\n--- Resultado Final ---")
print(f"El valor Máximo es: {maximo}")
print(f"El valor Mínimo es: {minimo}")
