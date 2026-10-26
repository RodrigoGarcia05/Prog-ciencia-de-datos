valores = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

romano = input("Ingrese un número romano: ").strip().upper()

if len(romano) == 0 or len(romano) >10:
    print("La cadena debe tener entre 1 y 10 caracteres.")
else: 
    arabigo= 0
    for i in range(len(romano)):
        valor_actual = valores[romano[i]]
        
        # si el simbolo es menor al siguiente, se resta ej IV = 4
        if i + 1 < len(romano) and valor_actual < valores[romano[i + 1]]:
            arabigo -= valor_actual
        else: 
            arabigo += valor_actual
            
print(f"Número romano: {romano}")
print(f"Número arabigo: {arabigo}")
