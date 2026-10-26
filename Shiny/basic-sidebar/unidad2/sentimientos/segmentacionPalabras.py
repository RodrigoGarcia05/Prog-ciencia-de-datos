# segmentamos el texto en palabras teniendo en cuenta los espacios
bible_tokens = bible.split()
# cargamos la versión de la Biblia segmentado en palabras
bible_words = gutenberg.words("bible-kjv.txt")

# no da el mismo número de tokens
print(len(bible_tokens), len(bible_words))

print(bible_tokens[:100])
print("\n", "-" * 75, "\n")
print(bible_words[:100])
