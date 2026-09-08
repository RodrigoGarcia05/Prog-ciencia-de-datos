#mostrar por pantalla las dimensiones del DataFrame 
print('Dimensiones', titanic.shape)
print('Numero de elementos', titanic.size)
print('Nombres de columnas', titanic.columns)
print('Nombres de filas', titanic.index)
print('Tipos de datos', titanic.dtypes)
print('Primeras 10 filas', titanic.head(10))
print('Ultimas 10 filas', titanic.tail(10))
