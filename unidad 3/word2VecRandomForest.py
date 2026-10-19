import numpy as np
from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier

# 1. Definir un corpus de ejemplo (oraciones tokenizadas) y sus etiquetas (y)
# Supongamos que queremos clasificar si una oración habla de animales/mascotas (1) o no (0)
sentencias = [
    ["el", "gato", "duerme", "en", "el", "sofa"],
    ["el", "perro", "corre", "en", "el", "jardin"],
    ["un", "gato", "y", "un", "perro", "son", "mascotas"],
    ["las", "mascotas", "juegan", "en", "el", "jardin"],
    ["el", "auto", "rojo", "corre", "en", "la", "pista"],
    ["la", "computadora", "funciona", "muy", "bien"]
]

# Etiquetas correspondientes (1 = Animal/Mascota, 0 = Otro contexto)
etiquetas = [1, 1, 1, 1, 0, 0]

# 2. Entrenar el modelo Word2Vec
modelo_w2v = Word2Vec(
    sentences=sentencias,
    vector_size=50,
    window=2,
    min_count=1,
    workers=4,
    sg=0  # 0 = CBOW, 1 = Skip-gram
)

# 3. Función para convertir oraciones en vectores (promediando los vectores de sus palabras)
def obtener_vector_oracion(oracion, modelo, vector_size):
    vectores = [modelo.wv[palabra] for palabra in oracion if palabra in modelo.wv]
    if len(vectores) == 0:
        return np.zeros(vector_size)
    return np.mean(vectores, axis=0)

# Construir la matriz de características (X) para el clasificador
vector_size = 50
X = np.array([obtener_vector_oracion(sent, modelo_w2v, vector_size) for sent in sentencias])
y = np.array(etiquetas)

# 4. Entrenar el modelo Random Forest
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X, y)

# 5. Probar el modelo con una nueva oración
nueva_oracion = ["el", "perro", "duerme"]
vector_nuevo = obtener_vector_oracion(nueva_oracion, modelo_w2v, vector_size)
prediccion = rf_classifier.predict([vector_nuevo])

print("--- RESULTADOS ---")
print(f"Predicción para la nueva oración {nueva_oracion}: {'Mascota/Animal (1)' if prediccion[0] == 1 else 'Otro (0)'}")
