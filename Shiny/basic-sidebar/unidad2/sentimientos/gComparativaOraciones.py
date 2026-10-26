sia = SentimentIntensityAnalyzer()
resultados = []

for libro in gutenberg.fileids():
    # VADER tiene un límite práctico por texto largo, por lo que una opción
    # común y representativa es calcular la media de las oraciones
    oraciones = gutenberg.sents(libro)
    print(oraciones)
    # Para optimizar el rendimiento y evitar sobrecarga de memoria,
    # unimos las palabras de cada oración para pasarlas por el analizador
    scores = [sia.polarity_scores(' '.join(oracion))['compound'] for oracion in oraciones]
    score_promedio = sum(scores) / len(scores)

    # Clasificación basada en el score compuesto promedio
    if score_promedio > 0.05:
        clasificacion = 'Positivo'
    elif score_promedio < -0.05:
        clasificacion = 'Negativo'
    else:
        clasificacion = 'Neutro'

    resultados.append({
        'Libro': libro[:-4],
        'Compound_Score': score_promedio,
        'Clasificacion': clasificacion
    })

# Convertir a DataFrame para facilitar la manipulación y graficado
df = pd.DataFrame(resultados)
print(df)

# Graficar los resultados
plt.figure(figsize=(10, 6))
colores = df['Clasificacion'].map({'Positivo': 'green', 'Negativo': 'red', 'Neutro': 'gray'})
plt.barh(df['Libro'], df['Compound_Score'], color=colores)
plt.axvline(x=0.05, color='green', linestyle='--', alpha=0.7, label='Límite Positivo (>0.05)')
plt.axvline(x=-0.05, color='red', linestyle='--', alpha=0.7, label='Límite Negativo (<-0.05)')
plt.title('Clasificación de Sentimientos de Libros de Gutenberg (VADER)')
plt.xlabel('Puntuación Compuesta Promedio')
plt.ylabel('Libros')
plt.legend()
plt.tight_layout()
plt.show()
