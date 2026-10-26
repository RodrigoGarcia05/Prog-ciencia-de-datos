# cargo la versión de Alicia segmentada en párrafos
alice_paras = gutenberg.paras("carroll-alice.txt")
print("Alice tiene", len(alice_paras), "párrafos")

# imprimo los cinco primeros
for para in alice_paras[:5]:
    print(para)
    print("\n", "-" * 75, "\n")
