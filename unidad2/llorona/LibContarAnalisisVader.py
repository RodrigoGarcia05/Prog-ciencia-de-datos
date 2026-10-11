#LIBRERIAS
import urllib.request
import re
import string
from collections import Counter
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# -*- coding: utf-8 -*-

import re
from collections import Counter
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Descargar léxico de VADER si no está instalado
nltk.download('vader_lexicon', quiet=True)

ARCHIVO = "/kaggle/input/datasets/rodrigogarciah/leyendallorona/la llorona.txt"

# Leer el archivo
with open(ARCHIVO, "r", encoding="utf-8") as f:
    texto = f.read()

# ---------------------------------------------------------
# 1. Contar total de palabras
# ---------------------------------------------------------
palabras = re.findall(r"\b\w+\b", texto, flags=re.UNICODE)
total_palabras = len(palabras)

print(f"Total de palabras del libro: {total_palabras}")

# ---------------------------------------------------------
# 2. Análisis de sentimiento con VADER
# ---------------------------------------------------------
sia = SentimentIntensityAnalyzer()

# Sentimiento global del texto completo
score_global = sia.polarity_scores(texto)
print("\nSentimiento global del texto:")
print(score_global)

# Análisis por oraciones
oraciones = re.split(r'(?<=[.!?…])\s+', texto)
resultados = []

for i, oracion in enumerate(oraciones, 1):
    if oracion.strip():
        scores = sia.polarity_scores(oracion)
        resultados.append((i, oracion.strip(), scores))

print("\nPrimeras 10 oraciones analizadas:")
for i, oracion, scores in resultados[:10]:
    print(f"{i:03d} | compound={scores['compound']:+.3f} | {oracion[:90]}...")

# Promedio compound
if resultados:
    promedio = sum(s['compound'] for _, _, s in resultados) / len(resultados)
    print(f"\nCompound promedio por oración: {promedio:.3f}")

# ---------------------------------------------------------
# 3. Palabras positivas y negativas según el léxico VADER
# ---------------------------------------------------------
lexicon = sia.lexicon

positivas = []
negativas = []

for palabra in palabras:
    p = palabra.lower()
    if p in lexicon:
        valor = lexicon[p]
        if valor > 0:
            positivas.append(p)
        elif valor < 0:
            negativas.append(p)

conteo_pos = Counter(positivas)
conteo_neg = Counter(negativas)

print(f"\nPalabras positivas detectadas: {len(positivas)}")
print("Top positivas:", conteo_pos.most_common(10))

print(f"\nPalabras negativas detectadas: {len(negativas)}")
print("Top negativas:", conteo_neg.most_common(10))

# ---------------------------------------------------------
# 4. Gráfica de palabras positivas vs negativas
# ---------------------------------------------------------
plt.figure(figsize=(6, 4))
barras = plt.bar(
    ["Positivas", "Negativas"],
    [len(positivas), len(negativas)],
    color=["#2e8b57", "#c0392b"]
)

plt.title("Palabras positivas y negativas según VADER")
plt.ylabel("Cantidad de palabras")

for barra, valor in zip(barras, [len(positivas), len(negativas)]):
    plt.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 0.1,
        str(valor),
        ha="center"
    )

plt.tight_layout()
plt.savefig("grafica_sentimiento_llorona.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 5. Gráfica opcional: top palabras positivas y negativas
# ---------------------------------------------------------
if positivas or negativas:
    top_pos = conteo_pos.most_common(10)
    top_neg = conteo_neg.most_common(10)

    plt.figure(figsize=(10, 4))

    if top_pos:
        plt.subplot(1, 2, 1)
        palabras_p, frec_p = zip(*top_pos)
        plt.barh(palabras_p, frec_p, color="#2e8b57")
        plt.title("Top palabras positivas")
        plt.xlabel("Frecuencia")

    if top_neg:
        plt.subplot(1, 2, 2)
        palabras_n, frec_n = zip(*top_neg)
        plt.barh(palabras_n, frec_n, color="#c0392b")
        plt.title("Top palabras negativas")
        plt.xlabel("Frecuencia")

    plt.tight_layout()
    plt.savefig("top_palabras_sentimiento_llorona.png", dpi=150)
    plt.show()
