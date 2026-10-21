# ESTRUCTURA DE UN PROGRAMA USANDO WORD2VEC (GENSIM)

# 1. IMPORTACIÓN DE LIBRERÍAS
# Se importa la clase principal Word2Vec desde la librería gensim
from gensim.models 
import Word2Vec

# 2. PREPARACIÓN DEL CORPUS (DATOS DE ENTRADA)
# Word2Vec requiere una lista de oraciones, donde cada oración 
# está previamente tokenizada (convertida en una lista de palabras/strings).
corpus_ejemplo = [
    ["aprender", "ciencia", "de", "datos", "es", "fascinante"],
    ["la", "programacion", "en", "python", "facilita", "el", "analisis"],
    ["los", "modelos", "de", "lenguaje", "procesan", "palabras"],
    ["la", "logica", "y", "la", "practica", "mejoran", "el", "codigo"]
]

# 3. ENTRENAMIENTO DEL MODELO WORD2VEC
# Se inicializa y entrena el modelo configurando sus hiperparámetros clave:
# - sentences: El corpus de texto tokenizado.
# - vector_size: El tamaño o dimensiones del vector (ej. 50, 100, 300).
# - window: La ventana de contexto (distancia máxima entre palabras).
# - min_count: Frecuencia mínima para ignorar palabras muy raras.
# - workers: Hilos de procesamiento para acelerar el entrenamiento.
# - sg: Algoritmo de entrenamiento (0 para CBOW, 1 para Skip-gram).
modelo = Word2Vec(
    sentences=corpus_ejemplo,
    vector_size=50,
    window=2,
    min_count=1,
    workers=2,
    sg=0
)

# 4. EXTRACCIÓN Y OPERACIONES CON EL ESPACIO VECTORIAL (modelo.wv)
# Una vez entrenado, se utiliza la propiedad .wv para consultar los vectores:

# A. Obtener el vector numérico asociado a una palabra específica
vector_palabra = modelo.wv["python"]
print("Primeros valores del vector:", vector_palabra[:3])

# B. Calcular la similitud semántica (coseno) entre dos palabras
similitud = modelo.wv.similarity("python", "datos")
print("Similitud:", similitud)

# C. Encontrar las palabras más cercanas o relacionadas a un término
palabras_similares = modelo.wv.most_similar("programacion", topn=2)
print("Palabras similares:", palabras_similares)

# 5. PERSISTENCIA DEL MODELO (OPCIONAL)
# Comandos estándar para guardar el modelo entrenado en disco y cargarlo después:
# modelo.save("mi_modelo_word2vec.model")
# modelo_cargado = Word2Vec.load("mi_modelo_word2vec.model")
