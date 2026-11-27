# -*- coding: utf-8 -*-
"""
ANÁLISIS DE SENTIMIENTO DE TWEETS – TAMPICO / MADERO
====================================================
Pipeline completo con NLTK:
  carga → (traducción opcional) → limpieza → tokenización → stopwords →
  TextBlob + VADER + SentiWordNet → consenso → variables para Power BI →
  gráficas + nubes de palabras → CSV final listo para Power BI.

Instalación (una sola vez):
    pip install -r requirements.txt

Estructura del proyecto:
    Analisis_Sentimiento_Tampico/
    ├── analisis_sentimiento_tweets.py
    ├── datos/tweets_tampico_madero_powerbi.csv
    └── resultados/
        ├── tweets_sentimiento_powerbi.csv   ← el archivo para Power BI
        └── graficas/*.png                   ← gráficas y nubes de palabras

Uso (en Mac usa python3):
    python3 analisis_sentimiento_tweets.py                     # usa datos/tweets_tampico_madero_powerbi.csv
    python3 analisis_sentimiento_tweets.py otro_archivo.csv
"""

# =============================================================================
# 1. LIBRERÍAS
# =============================================================================
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

# Librerías de apoyo
import os
import sys
import ssl
import html
import unicodedata
import warnings
from collections import Counter
import time
import threading

# --- Corrección SSL para macOS -----------------------------------------------
# El Python de python.org en Mac no trae certificados y nltk.download falla con
# "CERTIFICATE_VERIFY_FAILED". Usamos los certificados del paquete certifi.
try:
    import certifi
    ssl._create_default_https_context = lambda *a, **k: ssl.create_default_context(cafile=certifi.where())
except ImportError:
    print("⚠ Falta 'certifi' (pip install certifi). Si nltk.download falla con CERTIFICATE_VERIFY_FAILED, "
          "ejecuta: open \"/Applications/Python 3.13/Install Certificates.command\"")

# --- Recursos de NLTK (solo se descargan si faltan) ---------------------------
RECURSOS_NLTK = {
    'punkt': 'tokenizers/punkt',
    'punkt_tab': 'tokenizers/punkt_tab',          # las versiones nuevas de NLTK lo piden para word_tokenize
    'stopwords': 'corpora/stopwords',
    'vader_lexicon': 'sentiment/vader_lexicon.zip',
    'wordnet': 'corpora/wordnet',
    'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng': 'taggers/averaged_perceptron_tagger_eng',
    'sentiwordnet': 'corpora/sentiwordnet',
    'omw-1.4': 'corpora/omw-1.4',
}

def recurso_disponible(ruta):
    for r in (ruta, ruta.replace('.zip', ''), ruta + '.zip'):
        try:
            nltk.data.find(r)
            return True
        except LookupError:
            pass
    return False

faltantes = []
for paquete, ruta in RECURSOS_NLTK.items():
    if not recurso_disponible(ruta):
        nltk.download(paquete, quiet=True)
        if not recurso_disponible(ruta):
            faltantes.append(paquete)

# 'averaged_perceptron_tagger' (versión vieja) es opcional si existe la '_eng'
faltantes = [p for p in faltantes if p != 'averaged_perceptron_tagger']
if faltantes:
    sys.exit("\n✖ No se pudieron descargar estos recursos de NLTK: " + ", ".join(faltantes) +
             "\n  Solución en Mac: pip install certifi   (o ejecuta 'Install Certificates.command' "
             "de tu carpeta /Applications/Python 3.x) y vuelve a correr el script.")
print("✔ Recursos de NLTK listos")

warnings.filterwarnings('ignore')

try:
    from wordcloud import WordCloud
    HAY_WORDCLOUD = True
except ImportError:
    HAY_WORDCLOUD = False
    print("⚠ No está instalada 'wordcloud' (pip install wordcloud). Se omitirán las nubes de palabras.")


# =============================================================================
# 2. CONFIGURACIÓN
# =============================================================================
# Rutas relativas a la carpeta del proyecto (funciona sin importar desde dónde lo ejecutes)
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # en Jupyter no existe __file__
    BASE = os.getcwd()
RUTA_CSV = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.csv') \
    else os.path.join(BASE, 'datos', 'tweets_tampico_madero_powerbi.csv')
CARPETA_SALIDA = os.path.join(BASE, 'resultados')
CARPETA_GRAFICAS = os.path.join(CARPETA_SALIDA, 'graficas')
ARCHIVO_POWERBI = os.path.join(CARPETA_SALIDA, 'tweets_sentimiento_powerbi.csv')

# TextBlob, VADER y SentiWordNet SOLO entienden inglés. Los tweets están en español,
# así que por defecto se traducen al inglés antes de medir el sentimiento.
# Si no tienes internet o 'deep-translator', se analiza el texto original.
TRADUCIR_A_INGLES = True

# Si en Power BI los decimales salen mal (p. ej. 0.25 aparece como 25),
# cambia esto a ',' y el CSV se exportará con ';' como separador de columnas.
SEPARADOR_DECIMAL = '.'

# En Jupyter las gráficas se muestran en línea. En terminal solo se guardan como PNG
# (si se abrieran ventanas, el script se detendría hasta cerrar cada una).
MOSTRAR_GRAFICAS = 'ipykernel' in sys.modules
if not MOSTRAR_GRAFICAS:
    plt.switch_backend('Agg')

# Segundos máximos por traducción (si Google no responde, se usa el texto original)
TIMEOUT_TRADUCCION = 15

# Palabras sin valor para nubes de palabras (lugares y frases automáticas de Instagram/Foursquare)
STOPWORDS_EXTRA = {
    'tampico', 'madero', 'tamaulipas', 'mexico', 'cd', 'ciudad', 'tampicomadero',
    'acaba', 'publicar', 'foto', 'video', 'amp', 'lt', 'gt', 'rt', 'https', 'http', 'co',
    'in', 'en', 'via', 'q', 'x', 'jaja', 'jajaja',
}

# Negaciones: NO se quitan, porque cambian el sentido ("not good" ≠ "good")
NEGACIONES = {'no', 'not', 'nor', 'never', 'ni', 'nunca', 'jamas', 'tampoco'}

COLORES_SENT = {'Positive': '#2E9E5B', 'Neutral': '#9AA0A6', 'Negative': '#D64545'}
ORDEN_SENT = ['Positive', 'Neutral', 'Negative']
METODOS = ['TextBlob', 'VADER', 'SentiWordNet']

os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
sns.set_theme(style='whitegrid')


# =============================================================================
# 3. CARGA DE DATOS
# =============================================================================
print(f"\nCargando {RUTA_CSV} ...")
analisisSenti = pd.read_csv(RUTA_CSV, encoding='utf-8-sig')   # utf-8-sig ignora el BOM que agregan Excel/VS Code
analisisSenti = analisisSenti.rename(columns={'tweet': 'Content'})
analisisSenti = analisisSenti.dropna(subset=['Content']).reset_index(drop=True)
analisisSenti.insert(0, 'Tweet_ID', range(1, len(analisisSenti) + 1))
analisisSenti['timestamp'] = pd.to_datetime(analisisSenti['timestamp'], errors='coerce')
print(f"Tweets cargados: {len(analisisSenti)}")


# =============================================================================
# 4. TRADUCCIÓN AL INGLÉS (opcional)
# =============================================================================
def quitar_urls(text):
    return re.sub(r'http\S+', '', html.unescape(str(text))).strip()

analisisSenti['Texto_Ingles'] = analisisSenti['Content'].apply(quitar_urls)

if TRADUCIR_A_INGLES:
    try:
        from deep_translator import GoogleTranslator

        def traducir(text):
            try:
                return GoogleTranslator(source='auto', target='en').translate(text) or text
            except Exception:
                return text                     # si falla un tweet, se queda el original

        unicos = [t for t in analisisSenti['Texto_Ingles'].unique() if t.strip()]
        print(f"Traduciendo {len(unicos)} tweets al inglés (requiere internet)...")
        traducciones, fallidos = {}, 0
        # Hilos "daemon" en lotes de 8: si Google no responde, el script NO se queda colgado
        for inicio in range(0, len(unicos), 8):
            lote = unicos[inicio:inicio + 8]
            hilos = [threading.Thread(target=lambda t=t: traducciones.__setitem__(t, traducir(t)), daemon=True)
                     for t in lote]
            for h in hilos:
                h.start()
            limite = time.time() + TIMEOUT_TRADUCCION
            for h in hilos:
                h.join(max(0, limite - time.time()))
            for t in lote:
                if traducciones.setdefault(t, t) == t:
                    fallidos += 1
            print(f"   {min(inicio + 8, len(unicos))}/{len(unicos)}", end='\r')
        print(f"   Traducidos: {len(unicos) - fallidos}/{len(unicos)}"
              + (f"  ({fallidos} quedaron igual: ya estaban en inglés o no hubo respuesta)" if fallidos else ""))
        analisisSenti['Texto_Ingles'] = analisisSenti['Texto_Ingles'].map(lambda t: traducciones.get(t, t))
    except ImportError:
        print("⚠ No está instalada 'deep-translator' (pip install deep-translator). "
              "Se analizará el texto original en español.")


# =============================================================================
# 5. LIMPIEZA DE TEXTO, TOKENIZACIÓN Y STOPWORDS
# =============================================================================
def clean_text(text):
    text = html.unescape(str(text)).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)                          # menciones (@usuario)
    # Quitar acentos ANTES del filtro de letras: "día" → "dia" (si no, quedaría "da")
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    regex = r'[\!\”\#\$\%\&\\\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\\\]\^\_\`\{\|\}\~]'
    text = re.sub(regex, ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Mantener solo letras
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Limpiando texto...")
analisisSenti['Clean_Content'] = analisisSenti['Texto_Ingles'].apply(clean_text)

stop_words = (set(stopwords.words('english')) | set(stopwords.words('spanish'))) - NEGACIONES

def preprocess_tokens(text):
    tokens = word_tokenize(text)
    filtered = [w for w in tokens if not w in stop_words]
    return " ".join(filtered)

print("Tokenizando y removiendo stopwords...")
analisisSenti['Final_Content'] = analisisSenti['Clean_Content'].apply(preprocess_tokens)
analisisSenti['Num_Tokens'] = analisisSenti['Final_Content'].str.split().str.len().fillna(0).astype(int)

# Palabras clave en ESPAÑOL (texto original) para nubes de palabras y Power BI
stop_nube = set(stopwords.words('spanish')) | set(stopwords.words('english')) | STOPWORDS_EXTRA

def palabras_clave(text):
    tokens = word_tokenize(clean_text(text))
    return " ".join(w for w in tokens if w not in stop_nube and len(w) > 2)

analisisSenti['Palabras_Clave'] = analisisSenti['Content'].apply(palabras_clave)


# =============================================================================
# 6. ANÁLISIS DE SENTIMIENTO
# =============================================================================
# A. TextBlob
print("Aplicando TextBlob...")
analisisSenti['TextBlob_Score'] = analisisSenti['Final_Content'].apply(lambda x: TextBlob(x).sentiment.polarity)
analisisSenti['TextBlob_Analysis'] = analisisSenti['TextBlob_Score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

# B. VADER
print("Aplicando VADER...")
sia = SentimentIntensityAnalyzer()
analisisSenti['VADER_Score'] = analisisSenti['Final_Content'].apply(lambda x: sia.polarity_scores(x)['compound'])
analisisSenti['VADER_Analysis'] = analisisSenti['VADER_Score'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))

# C. SentiWordNet
print("Aplicando SentiWordNet... (El etiquetado gramatical puede demorar debido al volumen de datos)")
lemmatizer = WordNetLemmatizer()

# Función para mapear etiquetas POS de NLTK a etiquetas compatibles con WordNet
def penn_to_wn(tag):
    if tag.startswith('J'): return wn.ADJ
    elif tag.startswith('N'): return wn.NOUN
    elif tag.startswith('R'): return wn.ADV
    elif tag.startswith('V'): return wn.VERB
    return None

def get_sentiwordnet_score(text):
    sentiment_score = 0.0
    tokens = text.split()
    if not tokens: return 0.0

    # Etiquetado gramatical de la oración (POS tagging)
    tags = pos_tag(tokens)
    valid_words = 0

    for word, tag in tags:
        wn_tag = penn_to_wn(tag)
        if wn_tag not in (wn.NOUN, wn.ADJ, wn.ADV, wn.VERB): continue

        # Reducir la palabra a su raíz (lematización)
        lemma = lemmatizer.lemmatize(word, pos=wn_tag)
        if not lemma: continue

        synsets = wn.synsets(lemma, pos=wn_tag)
        if not synsets: continue

        # Tomar el significado más común
        synset = synsets[0]
        swn_synset = swn.senti_synset(synset.name())

        # Calcular el puntaje neto (Score Positivo - Score Negativo)
        sentiment_score += (swn_synset.pos_score() - swn_synset.neg_score())
        valid_words += 1

    # Retornar el promedio del sentimiento de la oración
    if valid_words > 0:
        return sentiment_score / valid_words
    return 0.0

analisisSenti['SentiWordNet_Score'] = analisisSenti['Final_Content'].apply(get_sentiwordnet_score)
analisisSenti['SentiWordNet_Analysis'] = analisisSenti['SentiWordNet_Score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))


# =============================================================================
# 7. CONSENSO ENTRE LOS 3 MÉTODOS (voto de mayoría)
# =============================================================================
print("Calculando consenso...")

def consenso(row):
    votos = Counter(row[f'{m}_Analysis'] for m in METODOS).most_common()
    etiqueta, n = votos[0]
    return pd.Series({'Sentiment_Final': etiqueta if n >= 2 else 'Neutral',   # empate 1-1-1 → Neutral
                      'Acuerdo_Metodos': n})                                   # 3 = unánime, 2 = mayoría, 1 = sin acuerdo

analisisSenti[['Sentiment_Final', 'Acuerdo_Metodos']] = analisisSenti.apply(consenso, axis=1)
analisisSenti['Score_Promedio'] = analisisSenti[[f'{m}_Score' for m in METODOS]].mean(axis=1)

MAPA_ES = {'Positive': 'Positivo', 'Neutral': 'Neutral', 'Negative': 'Negativo'}
analisisSenti['Sentimiento'] = analisisSenti['Sentiment_Final'].map(MAPA_ES)
analisisSenti['Sentimiento_Num'] = analisisSenti['Sentiment_Final'].map({'Positive': 1, 'Neutral': 0, 'Negative': -1})
analisisSenti['Nivel_Acuerdo'] = analisisSenti['Acuerdo_Metodos'].map({3: 'Unánime (3/3)', 2: 'Mayoría (2/3)', 1: 'Sin acuerdo'})


# =============================================================================
# 8. VARIABLES EXTRA PARA POWER BI
# =============================================================================
print("Generando variables para Power BI...")
ts = analisisSenti['timestamp']
DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
analisisSenti['Fecha'] = ts.dt.date
analisisSenti['Hora'] = ts.dt.hour
analisisSenti['Dia_Semana'] = ts.dt.dayofweek.map(dict(enumerate(DIAS)))
analisisSenti['Num_Dia_Semana'] = ts.dt.dayofweek + 1              # 1 = lunes (para ordenar)
analisisSenti['Franja_Horaria'] = pd.cut(ts.dt.hour, bins=[-1, 5, 11, 18, 23],
                                         labels=['Madrugada', 'Mañana', 'Tarde', 'Noche']).astype(str)

analisisSenti['Usuario'] = analisisSenti['user']
analisisSenti['Num_Palabras'] = analisisSenti['Content'].apply(lambda t: len(quitar_urls(t).split()))
analisisSenti['Num_Hashtags'] = analisisSenti['Content'].str.count(r'#\w+')
analisisSenti['Num_Menciones'] = analisisSenti['Content'].str.count(r'@\w+')
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]')
analisisSenti['Num_Emojis'] = analisisSenti['Content'].apply(lambda t: len(EMOJI_RE.findall(str(t))))
analisisSenti['Hashtags'] = analisisSenti['Content'].apply(lambda t: ' '.join(re.findall(r'#\w+', str(t))).lower())

# Lugar mencionado en el tweet ("... en Tampico https://", "@ El Porvenir Restaurante https://")
PAT_AT = re.compile(r'@\s+([A-ZÁÉÍÓÚÑ][^#@\n…()]*?)\s*(?:\(|\)|…|https|$)')
PAT_EN = re.compile(r'\ben\s+([A-ZÁÉÍÓÚÑ][^#@\n…]*?)\s*(?:…|https|$)')

def extraer_lugar(text):
    text = str(text)
    m = PAT_AT.findall(text) or PAT_EN.findall(text)
    if not m:
        return 'Sin lugar'
    lugar = re.sub(r'\s+in\s+Tampico.*$', '', m[-1]).strip(' ,.-')
    for completo in ['Tampico', 'Ciudad Madero']:                   # nombres truncados por Twitter ("Tamp…")
        if len(lugar) >= 4 and completo.startswith(lugar):
            return completo
    return lugar or 'Sin lugar'

analisisSenti['Lugar'] = analisisSenti['Content'].apply(extraer_lugar)

# Idioma = el que más se repite entre los 3 detectores (si no coinciden, gana langdetect)
cols_lang = [c for c in ['lang_langdetect', 'lang_textblob', 'lang_langid'] if c in analisisSenti.columns]
if cols_lang:
    def idioma(row):
        etiqueta, n = Counter(row[cols_lang].dropna()).most_common(1)[0] if row[cols_lang].notna().any() else ('desconocido', 0)
        return etiqueta if n >= 2 else row[cols_lang[0]]
    analisisSenti['Idioma'] = analisisSenti.apply(idioma, axis=1)

# Tweets repetidos (mismo usuario + mismo texto sin link) → útil para filtrar spam
analisisSenti['Es_Duplicado'] = analisisSenti.assign(_t=analisisSenti['Content'].apply(quitar_urls)) \
                                             .duplicated(subset=['user', '_t'], keep='first') \
                                             .map({True: 'Sí', False: 'No'})


# =============================================================================
# 9. GRÁFICAS Y NUBES DE PALABRAS
# =============================================================================
print("Generando gráficas...")

def guardar(fig, nombre):
    fig.savefig(os.path.join(CARPETA_GRAFICAS, nombre), dpi=150, bbox_inches='tight')
    if MOSTRAR_GRAFICAS:
        plt.show()
    plt.close(fig)

# 9.1 Distribución de sentimiento por método
largo = pd.concat([pd.DataFrame({'Método': m, 'Sentimiento': analisisSenti[f'{m}_Analysis']}) for m in METODOS])
fig, ax = plt.subplots(figsize=(9, 5))
sns.countplot(data=largo, x='Método', hue='Sentimiento', hue_order=ORDEN_SENT, palette=COLORES_SENT, ax=ax)
for c in ax.containers:
    ax.bar_label(c, fontsize=9)
ax.set_title('Clasificación de sentimiento por método', fontsize=14, weight='bold')
ax.set_ylabel('Número de tweets'); ax.set_xlabel('')
guardar(fig, '01_sentimiento_por_metodo.png')

# 9.2 Sentimiento final (consenso)
conteo = analisisSenti['Sentiment_Final'].value_counts().reindex(ORDEN_SENT, fill_value=0)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(conteo.index, conteo.values, color=[COLORES_SENT[s] for s in conteo.index])
for i, v in enumerate(conteo.values):
    axes[0].text(i, v, str(v), ha='center', va='bottom', fontsize=11)
axes[0].set_title('Sentimiento final (consenso)', weight='bold'); axes[0].set_ylabel('Tweets')
conteo_nz = conteo[conteo > 0]
axes[1].pie(conteo_nz.values, labels=conteo_nz.index, autopct='%1.1f%%', startangle=90,
            colors=[COLORES_SENT[s] for s in conteo_nz.index], wedgeprops={'width': 0.45, 'edgecolor': 'white'})
axes[1].set_title('Proporción del sentimiento final', weight='bold')
guardar(fig, '02_sentimiento_final.png')

# 9.3 Distribución de los puntajes
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
for ax, m in zip(axes, METODOS):
    sns.histplot(analisisSenti[f'{m}_Score'], bins=20, kde=True, color='#4C72B0', ax=ax)
    ax.axvline(0, color='black', ls='--', lw=1)
    ax.set_title(f'Puntajes {m}', weight='bold'); ax.set_xlabel('Score')
guardar(fig, '03_distribucion_scores.png')

# 9.4 Correlación entre métodos
fig, ax = plt.subplots(figsize=(6, 5))
corr = analisisSenti[[f'{m}_Score' for m in METODOS]].corr()
corr.index = corr.columns = METODOS
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn', vmin=-1, vmax=1, ax=ax)
ax.set_title('Correlación entre métodos', weight='bold')
guardar(fig, '04_correlacion_metodos.png')

# 9.5 Sentimiento por tweet (score promedio de cada tweet)
orden = analisisSenti.sort_values('Score_Promedio')
fig, ax = plt.subplots(figsize=(10, max(6, len(orden) * 0.22)))
ax.barh(orden['Tweet_ID'].astype(str), orden['Score_Promedio'],
        color=[COLORES_SENT[s] for s in orden['Sentiment_Final']])
ax.axvline(0, color='black', lw=0.8)
ax.set_title('Score promedio de sentimiento por tweet', weight='bold')
ax.set_xlabel('Score promedio (TextBlob, VADER, SentiWordNet)'); ax.set_ylabel('Tweet_ID')
ax.tick_params(axis='y', labelsize=7)
guardar(fig, '05_score_por_tweet.png')

# 9.6 Evolución en el tiempo
por_fecha = analisisSenti.groupby(['Fecha', 'Sentiment_Final']).size().unstack(fill_value=0) \
                         .reindex(columns=ORDEN_SENT, fill_value=0)
fig, ax = plt.subplots(figsize=(10, 5))
por_fecha.plot(kind='bar', stacked=True, color=[COLORES_SENT[s] for s in por_fecha.columns], ax=ax)
ax2 = ax.twinx()
ax2.plot(range(len(por_fecha)), analisisSenti.groupby('Fecha')['Score_Promedio'].mean().values,
         color='black', marker='o', label='Score promedio')
ax2.axhline(0, color='black', ls=':', lw=0.8); ax2.set_ylabel('Score promedio'); ax2.grid(False)
ax.legend(title='Sentimiento', loc='upper left')
ax.set_title('Sentimiento por fecha', weight='bold'); ax.set_ylabel('Tweets'); ax.set_xlabel('')
ax.tick_params(axis='x', rotation=45)
guardar(fig, '06_sentimiento_por_fecha.png')

# 9.7 Sentimiento por hora del día
por_hora = analisisSenti.groupby(['Hora', 'Sentiment_Final']).size().unstack(fill_value=0) \
                        .reindex(index=range(24), columns=ORDEN_SENT, fill_value=0)
fig, ax = plt.subplots(figsize=(11, 4.5))
por_hora.plot(kind='bar', stacked=True, color=[COLORES_SENT[s] for s in por_hora.columns], ax=ax, width=0.85)
ax.set_title('Sentimiento por hora del día', weight='bold'); ax.set_xlabel('Hora'); ax.set_ylabel('Tweets')
ax.tick_params(axis='x', rotation=0)
guardar(fig, '07_sentimiento_por_hora.png')

# 9.8 Sentimiento por usuario (top 10 usuarios más activos)
top_users = analisisSenti['Usuario'].value_counts().head(10).index
por_user = analisisSenti[analisisSenti['Usuario'].isin(top_users)] \
    .groupby(['Usuario', 'Sentiment_Final']).size().unstack(fill_value=0) \
    .reindex(index=top_users[::-1], columns=ORDEN_SENT, fill_value=0)
fig, ax = plt.subplots(figsize=(10, 6))
por_user.plot(kind='barh', stacked=True, color=[COLORES_SENT[s] for s in por_user.columns], ax=ax)
ax.set_title('Sentimiento de los 10 usuarios más activos', weight='bold'); ax.set_xlabel('Tweets'); ax.set_ylabel('')
guardar(fig, '08_sentimiento_por_usuario.png')

# 9.9 Palabras más frecuentes
todas = ' '.join(analisisSenti['Palabras_Clave']).split()
top_palabras = pd.DataFrame(Counter(todas).most_common(20), columns=['Palabra', 'Frecuencia'])
if not top_palabras.empty:
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.barplot(data=top_palabras, y='Palabra', x='Frecuencia', color='#4C72B0', ax=ax)
    ax.set_title('20 palabras más frecuentes', weight='bold')
    guardar(fig, '09_top_palabras.png')

# 9.10 Nubes de palabras (general, positiva, negativa, neutral)
if HAY_WORDCLOUD:
    nubes = [('General', analisisSenti, 'viridis'),
             ('Positivos', analisisSenti[analisisSenti['Sentiment_Final'] == 'Positive'], 'Greens'),
             ('Negativos', analisisSenti[analisisSenti['Sentiment_Final'] == 'Negative'], 'Reds'),
             ('Neutrales', analisisSenti[analisisSenti['Sentiment_Final'] == 'Neutral'], 'Greys')]
    for nombre, sub, cmap in nubes:
        texto = ' '.join(sub['Palabras_Clave']).strip()
        if not texto:
            print(f"   (sin palabras para la nube '{nombre}')")
            continue
        wc = WordCloud(width=1200, height=600, background_color='white', colormap=cmap,
                       max_words=150, collocations=False).generate(texto)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear'); ax.axis('off')
        ax.set_title(f'Nube de palabras – Tweets {nombre} ({len(sub)})', fontsize=14, weight='bold')
        guardar(fig, f'10_nube_{nombre.lower()}.png')


# =============================================================================
# 10. EXPORTAR CSV PARA POWER BI
# =============================================================================
columnas_powerbi = [
    'Tweet_ID', 'timestamp', 'Fecha', 'Hora', 'Dia_Semana', 'Num_Dia_Semana', 'Franja_Horaria',
    'Usuario', 'Content', 'Texto_Ingles', 'Final_Content', 'Palabras_Clave', 'Hashtags', 'Lugar',
    'latitude', 'longitude', 'Idioma',
    'Num_Palabras', 'Num_Tokens', 'Num_Hashtags', 'Num_Menciones', 'Num_Emojis', 'Es_Duplicado',
    'TextBlob_Score', 'TextBlob_Analysis',
    'VADER_Score', 'VADER_Analysis',
    'SentiWordNet_Score', 'SentiWordNet_Analysis',
    'Score_Promedio', 'Sentiment_Final', 'Sentimiento', 'Sentimiento_Num',
    'Acuerdo_Metodos', 'Nivel_Acuerdo',
]
columnas_powerbi = [c for c in columnas_powerbi if c in analisisSenti.columns]
salida = analisisSenti[columnas_powerbi].copy()

salida = salida.rename(columns={'timestamp': 'Fecha_Hora', 'Content': 'Tweet',
                                'latitude': 'Latitud', 'longitude': 'Longitud'})
salida['Fecha_Hora'] = pd.to_datetime(salida['Fecha_Hora']).dt.strftime('%Y-%m-%d %H:%M:%S')
salida['Fecha'] = pd.to_datetime(salida['Fecha']).dt.strftime('%Y-%m-%d')
for col in ['TextBlob_Score', 'VADER_Score', 'SentiWordNet_Score', 'Score_Promedio']:
    salida[col] = salida[col].round(4)
# Saltos de línea dentro de un tweet rompen la lectura del CSV en algunos visores
for col in ['Tweet', 'Texto_Ingles']:
    salida[col] = salida[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True)

sep = ';' if SEPARADOR_DECIMAL == ',' else ','
salida.to_csv(ARCHIVO_POWERBI, index=False, encoding='utf-8-sig', sep=sep, decimal=SEPARADOR_DECIMAL)


# =============================================================================
# 11. RESUMEN
# =============================================================================
print("\n" + "=" * 60)
print("RESUMEN DEL ANÁLISIS")
print("=" * 60)
print(f"Tweets analizados: {len(salida)}  |  Usuarios únicos: {salida['Usuario'].nunique()}")
for m in METODOS:
    dist = analisisSenti[f'{m}_Analysis'].value_counts().reindex(ORDEN_SENT, fill_value=0)
    print(f"  {m:<13} → " + "  ".join(f"{k}: {v}" for k, v in dist.items()))
dist = analisisSenti['Sentiment_Final'].value_counts().reindex(ORDEN_SENT, fill_value=0)
print(f"  {'CONSENSO':<13} → " + "  ".join(f"{k}: {v}" for k, v in dist.items()))
print(f"\nAcuerdo unánime entre los 3 métodos: {(analisisSenti['Acuerdo_Metodos'] == 3).mean():.0%} de los tweets")
print(f"\n✔ CSV para Power BI: {os.path.abspath(ARCHIVO_POWERBI)}")
print(f"✔ Gráficas (PNG):    {os.path.abspath(CARPETA_GRAFICAS)}")
