import numpy as np
from random import random, randint, sample


def knapsack(peso_permitido, pesos, valores):
    assert len(pesos) == len(valores)
    peso_total = sum(pesos)
    valor_total = sum(valores)
# Si la suma de pesos cabe en la mochila, devuelve la suma 
# total de valores directamente.
    if peso_total < peso_permitido: 
        return valor_total
    else:
#diccionario para almacenar los problemas
# W: capicidad disponible | i el numero de objetos considerados
        V = dict()
        for w in range(peso_permitido + 1):
            V[(w, 0)] = 0
        for i in range(len(pesos)):
            peso = pesos[i]
            valor = valores[i]
            for w in range(peso_permitido + 1):
                cand = V.get((w - peso, i), -float('inf')) + valor
# para cada objeto, compara no incluirlo frence a incluirlo
# devuélve el valor maximo alcanzable 
                V[(w, i + 1)] = max(V[(w, i)], cand)
        return max(V.values())

#evalua si el peso total es menor o igual al de la capacidad 
#mediante producto interno (np.inner)
def factible(seleccion, pesos, capacidad):
    return np.inner(seleccion, pesos) <= capacidad

#calcula ganancia total sumando los valores de los 
#objetos seleccionados.
def objetivo(seleccion, valores):
    return np.inner(seleccion, valores)

# aplicar min- max a un arreglo de Numpy para transofmrar cualquier distribución 
# al rango [0, 1].
def normalizar(data):
    menor = min(data)
    mayor = max(data)
    rango  = mayor - menor
    data = data - menor # > 0
    return data / rango # entre 0 y 1

# generador datos aleatorios con distribución normal 
# el valor de cada objeto esta correlaciónado con su peso (pesado tiende a valer mas)
def generador_pesos(cuantos, low, high):
    return np.round(normalizar(np.random.normal(size = cuantos)) * (high - low) + low)
 
def generador_valores(pesos, low, high):
    n = len(pesos)
    valores = np.empty((n))
    for i in range(n):
        valores[i] = np.random.normal(pesos[i], random())
    return normalizar(valores) * (high - low) + low

# genera matriz tamaño (tam, n) con 0s y 1s distribuidos uniformemente 
def poblacion_inicial(n, tam):
    pobl = np.zeros((tam, n))
    for i in range(tam):
        pobl[i] = (np.round(np.random.uniform(size = n))).astype(int)
    return pobl

# selecciona un objeto al azar dentro de un individuo e invierte su estado 
# (0 -> 1) 0 (1 ->0)
def mutacion(sol, n):
    pos = randint(0, n - 1)
    mut = np.copy(sol)
    mut[pos] = 1 if sol[pos] == 0 else 0
    return mut

#realiza un cruce de un solo punto 
#elige un punto de corte al azar, evitando los extremos
# corta ambos padres  en una posición aleatoria (pos)
# y recombina sus partes para generar 2 hijos totalmente nuevos
def reproduccion(x, y, n):
    pos = randint(2, n - 2)
    xy = np.concatenate([x[:pos], y[pos:]])
    yx = np.concatenate([y[:pos], x[pos:]])
    return (xy, yx)

# define n = 20 objetos disponibles
# init= 30 población baseline siempre sera de 30 mochilas
# asigna capcidad del contenedor al 65% del peso total disponible 
# rep=10 se realizan 10 cruces por generacion (genera 20 hijos en total)
# probabilidad de mutacion por individuo (pm) = 0.05
# Limite de 15 generaciones (tmax) proceso evolutivo se repetira durante 15 generaciones

n = 20
pesos = generador_pesos(n, 15, 80)
valores = generador_valores(pesos, 10, 500)
capacidad = int(round(sum(pesos) * 0.65))
optimo = knapsack(capacidad, pesos, valores)
init = 30
p = poblacion_inicial(n, init)
tam = p.shape[0]
assert tam == init
pm = 0.05
rep = 10
tmax = 15

# si un numero aleatorio es menor a pm, genera una mutación y la agrega a la población 
# usando np.stack

# selecciona parejas aleatorias con sample y agrega a sus hijos a la matriz de población 

# evalua a toda la población en un dataframe 
#ordena jerarquicamente priorizando que las soluciones factibles y entre ellas, las de mayor valor

#se queda unicamente con los mejores 30 individuos (init) para la siguiente generación
# manteniendo el tamaño de la población constante. 
import pandas as pd
d = None
for t in range(tmax):
    for i in range(tam): # mutarse con probabilidad pm
        if random() < pm:
            p = np.vstack([p, mutacion(p[i], n)])
# revisa las 30 mochilas, si random()< 0.05, crea una version mutada (invierte bit al azar)
# y lo agrega a la lista con np.stack
    for i in range(rep):  # reproducciones
        padres = sample(range(tam), 2)
        hijos = reproduccion(p[padres[0]], p[padres[1]], n)
        p = np.vstack([p, hijos[0], hijos[1]])
    tam = p.shape[0]
    d = []
#selecciona 2 padres al azar de la lista 10 veces (rep=10) 
#genera 2 hijos por cada pareja y los agrega a la lista"

#ahora la lista p tiene mas de 30 elementos 
# aprox 50 0 55 entre padres, mutantes e hijos
    for i in range(tam):
        d.append({'idx': i, 'obj': objetivo(p[i], valores),
                  'fact': factible(p[i], pesos, capacidad)})
    d = pd.DataFrame(d).sort_values(by = ['fact', 'obj'], ascending = False)
#fact: ¿Respeta el limite de peso? (true or false)
#obj: ¿Cuanto valor suma en total?

#ordena la tabla priorizando las mochilas que SI cumplen el peso (fact= True) y las de mayor valor

    mantener = np.array(d.idx[:init])
# toma unicamente el indice de los mejores 30 y desecha las demas. 
# La lista vuelve a quedar exactamente con 30 mochilas para iniciar el siguiente ciclo 

    p = p[mantener, :]
    tam = p.shape[0]
    assert tam == init
factibles = d.loc[d.fact == True,]
mejor = max(factibles.obj)
print(mejor, (optimo - mejor) / optimo)

#al terminar las generaciones, filtra las mochilas validas finales, obtiene la mejor ganancia alcanzada
#toma el valor de la mejor mochila encontrada (mejor)
#por el algoritmo genetico y calcula el erorr relativo contra la solucion optima exacta

# Error relativo = optimo - mejor / optimo 
