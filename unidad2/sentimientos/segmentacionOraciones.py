import nltk
nltk.download('punkt_tab')

# cargo la versión de Alicia segmentada en oraciones
alice_sents = gutenberg.sents("carroll-alice.txt")
print("Alice tiene", len(alice_sents), "oraciones")
print(alice_sents[2:5])  # imprimo la tercera, cuarta y quinta oración
