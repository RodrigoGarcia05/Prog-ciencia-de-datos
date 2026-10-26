

def generar_fibonacci(n):
    # casos base para valores pequeños
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    # se inicia el vector con los dos primeros términos de la serie
    vector_fib = [0, 1]
    
    # se generan los elementos restantes hasta completar n
    for i in range(2, n):
        siguiente = vector_fib[i - 1] + vector_fib[i - 2]
        vector_fib.append(siguiente)
        
    return vector_fib

try:
    n = int(input("¿Cuántos números de la serie de fibonacci desea generar?: "))
    
    if n < 1:
        print("Por favor, ingresa un número entero positivo mayor a 0.")
    else:
        # crea y llena el vector
        vector = generar_fibonacci(n)
        
        # muestra el resultado
        print(f"\nVector unidimensional con {n} elementos de Fibonacci:")
        print(vector)

except ValueError:
    print("Error: Debes ingresar un número entero válido.")
