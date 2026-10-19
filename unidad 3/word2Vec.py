from gensim.models import Word2Vec

# 1. Definir un corpus de ejemplo (oraciones tokenizadas en listas de palabras)
sentencias = [
    ["el", "gato", "duerme", "en", "el", "sofa"],
    ["el", "perro", "corre", "en", "el", "jardin"],
    ["un", "gato", "y", "un", "perro", "son", "mascotas"],
    ["las", "mascotas", "juegan", "en", "el", "jardin"]
]

# 2. Entrenar el modelo Word2Vec
# vector_size: dimensiones del vector
# window: distancia máxima entre la palabra actual y la predicha
# min_count: frecuencia mínima para considerar una palabra
# sg: 0 para CBOW, 1 para Skip-gram
modelo = Word2Vec(
    sentences=sentencias,
    vector_size=50,
    window=2,
    min_count=1,
    workers=4,
    sg=0  # 0 = CBOW, 1 = Skip-gram
)

# 3. Obtener el vector de una palabra específica
vector_gato = modelo.wv["gato"]
print("Vector de 'gato':", vector_gato[:5])  # Imprime los primeros 5 valores

# 4. Calcular la similitud semántica entre dos palabras
similitud = modelo.wv.similarity("gato", "perro")
print(f"Similitud entre 'gato' y 'perro': {similitud:.4f}")

# 5. Encontrar las palabras más similares a otra
mas_similares = modelo.wv.most_similar("mascotas", topn=2)
print("Palabras similares a 'mascotas':", mas_similares)
