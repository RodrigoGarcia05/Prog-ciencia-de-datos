# cargo la vesión 'cruda' de un par de libros. Como son libros del Proyecto Gutenberg, se trata de ficheros en texto plano
alice = gutenberg.raw("carroll-alice.txt")
print(alice[:200])  # imprimo los primeros 200 caracteres del libro de Alicia

print("-" * 70)

bible = gutenberg.raw("bible-kjv.txt")
print(bible[:200])  # imprimo los primeros 200 caracteres de la Biblia
