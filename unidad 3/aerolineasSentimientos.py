import pandas as pd
import nltk

# 1. Cargar el dataset de tweets
print("--- 1. CARGANDO DATSET ---")
tweetsAero = pd.read_csv('Tweets.csv')

# Tomamos una muestra de 100 tweets para agilizar la prueba
muestra_tweets = tweetsAero[['airline', 'text', 'airline_sentiment']].head(100).copy()
textos_muestra = muestra_tweets['text'].tolist()


# ==========================================
# MÉTODO 1: ANÁLISIS CON VADER (NLTK)
# ==========================================
print("\n--- 2. APLICANDO VADER ---")
nltk.download('vader_lexicon', quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

pred_vader = []
for texto in textos_muestra:
  scores = sia.polarity_scores(texto)
  compound = scores['compound']
  # Clasificación basada en el puntaje compound estándar
  if compound >= 0.05:
    pred_vader.append('positive')
  elif compound <= -0.05:
    pred_vader.append('negative')
  else:
    pred_vader.append('neutral')

muestra_tweets['pred_vader'] = pred_vader


# ==========================================
# MÉTODO 2: RECOMENDADO POR LA MÁQUINA (DEFAULT)
# ==========================================
print("\n--- 3. APLICANDO MODELO AUTOMÁTICO (TRANSFORMERS DEFAULT) ---")
from transformers import pipeline

# Pipeline sin definir modelo (la máquina decide sola)
clasificador_default = pipeline('sentiment-analysis')

# Investigar e imprimir qué modelo cargó la librería por defecto
nombre_modelo_default = clasificador_default.model.name_or_path
arquitectura_default = clasificador_default.model.config.architectures[0]
etiquetas_default = list(clasificador_default.model.config.id2label.values())

print('INFORMACIÓN DEL MODELO POR DEFECTO DE TRANSFORMERS:')
print(f'-> Modelo asignado automáticamente: {nombre_modelo_default}')
print(f'-> Arquitectura de red neuronal:    {arquitectura_default}')
print(f'-> Clases que predice:              {etiquetas_default}')

# Predicciones con el modelo por defecto
predicciones_def = clasificador_default(
    textos_muestra, truncation=True, max_length=128
)
muestra_tweets['pred_default'] = [
    p['label'].lower().replace('label_', '') for p in predicciones_def
]
muestra_tweets['score_default'] = [
    round(p['score'], 4) for p in predicciones_def
]


# ==========================================
# MÉTODO 3: ELEGIDO POR NOSOTROS (ESPECÍFICO)
# ==========================================
print(
    '\n--- 4. APLICANDO MODELO ELEGIDO POR NOSOTROS (RoBERTa para Tweets) ---'
)

# Modelo recomendado: especializado en Twitter y compatible con 3 clases
modelo_personalizado = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
clasificador_custom = pipeline(
    'sentiment-analysis', model=modelo_personalizado
)

print(f'-> Modelo seleccionado por nosotros: {modelo_personalizado}')
print(
    '-> Arquitectura: RoBERTa optimizado para redes sociales (3 clases:'
    ' negative, neutral, positive)'
)

# Predicciones con nuestro modelo elegido
predicciones_custom = clasificador_custom(
    textos_muestra, truncation=True, max_length=128
)
muestra_tweets['pred_elegido'] = [
    p['label'].lower() for p in predicciones_custom
]
muestra_tweets['score_elegido'] = [
    round(p['score'], 4) for p in predicciones_custom
]


# ==========================================
# 5. COMPARATIVA DE RESULTADOS
# ==========================================
print('\n--- 5. COMPARATIVA DE LOS PRIMEROS 5 TWEETS ---')
columnas_mostrar = [
    'airline_sentiment',
    'pred_vader',
    'pred_default',
    'pred_elegido',
    'text',
]
print(muestra_tweets[columnas_mostrar].head(5).to_string(index=False))
