# =========================================================
# 1. LIBRERÍAS
# =========================================================
import os
import re
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud

from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import (
    train_test_split, GridSearchCV, StratifiedKFold, cross_val_score
)
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    precision_score, recall_score, f1_score, accuracy_score,
    roc_curve, auc, roc_auc_score
)
from sklearn.preprocessing import label_binarize


for pkg in ["punkt", "punkt_tab", "stopwords", "vader_lexicon"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

sns.set_theme(style="whitegrid")


from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier

# =========================================================
# 5. Word2Vec + Random Forest (clasificación del sentimiento)
# =========================================================
X_tokens = df["tokens"]
y = df["sentimiento"]

# Split estratificado usando los tokens limpios
X_train_tokens, X_test_tokens, y_train, y_test = train_test_split(
    X_tokens, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\nTrain: {len(X_train_tokens)}  |  Test: {len(X_test_tokens)}")
print("Clases:", sorted(y.unique()))

# ---- Entrenamiento de Word2Vec ----
print("\nEntrenando modelo Word2Vec...")
w2v_model = Word2Vec(
    sentences=X_train_tokens, 
    vector_size=100,  # Dimensión de los vectores de palabras
    window=5,         # Ventana de contexto
    min_count=2,      # Frecuencia mínima de la palabra para ser considerada
    workers=4,
    seed=42
)

# Función para convertir una lista de tokens en un vector promedio del tweet
def obtener_vector_tweet(tokens, model, vector_size=100):
    vector = np.zeros(vector_size)
    contador = 0
    for palabra in tokens:
        if palabra in model.wv:
            vector += model.wv[palabra]
            contador += 1
    if contador > 0:
        vector = vector / contador
    return vector

# Transformar los datasets de entrenamiento y prueba a matrices de vectores
X_train_vecs = np.array([obtener_vector_tweet(tokens, w2v_model, vector_size=100) for tokens in X_train_tokens])
X_test_vecs = np.array([obtener_vector_tweet(tokens, w2v_model, vector_size=100) for tokens in X_test_tokens])

# ---- Clasificador Random Forest ----
rf_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    class_weight="balanced", # Útil para balancear clases en tweets
    random_state=42,
    n_jobs=-1
)

print("\nEntrenando Random Forest...")
rf_classifier.fit(X_train_vecs, y_train)

# ---- Predicciones ----
y_pred  = rf_classifier.predict(X_test_vecs)
y_proba = rf_classifier.predict_proba(X_test_vecs)

# ---- Métricas ----
print("\n===== MÉTRICAS RANDOM FOREST + WORD2VEC (configuración inicial) =====")
print(f"Accuracy           : {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision (weighted): {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
print(f"Recall    (weighted): {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
print(f"F1        (weighted): {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
print("\nReporte por clase:")
print(classification_report(y_test, y_pred, zero_division=0))

# ---- Matriz de confusión ----
LABELS = ["Negativo", "Neutro", "Positivo"]
cm = confusion_matrix(y_test, y_pred, labels=LABELS)
disp = ConfusionMatrixDisplay(cm, display_labels=LABELS)
fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(cmap="Blues", ax=ax, colorbar=False)
plt.title("Matriz de Confusión — Random Forest (Word2Vec)")
plt.show()

# ---- Curva ROC (One-vs-Rest, multiclase) ----
classes   = rf_classifier.classes_
y_bin     = label_binarize(y_test, classes=classes)

fig, ax = plt.subplots(figsize=(8, 6))
for i, cls in enumerate(classes):
    fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, lw=2, label=f"{cls} (AUC = {roc_auc:.3f})")

# Línea diagonal (azar)
ax.plot([0, 1], [0, 1], "k--", lw=1)
ax.set_xlabel("Tasa de Falsos Positivos (FPR)")
ax.set_ylabel("Tasa de Verdaderos Positivos (TPR)")
ax.set_title("Curvas ROC One-vs-Rest — Random Forest (Word2Vec)")
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()

# AUC macro
try:
    auc_macro = roc_auc_score(y_bin, y_proba, average="macro", multi_class="ovr")
    print(f"\nROC-AUC (macro, OvR): {auc_macro:.4f}")
except Exception as e:
    print("No se pudo calcular ROC-AUC macro:", e)


# =========================================================
# 6. HIPERPARAMETRIZACIÓN (validar si hay mejor configuración)
# =========================================================
# Buscamos sobre los hiperparámetros de Random Forest:
#  - n_estimators (número de árboles en el bosque)
#  - max_depth (profundidad máxima de los árboles)
#  - min_samples_split (mínimo de muestras requeridas para dividir un nodo)

param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    estimator=RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1),
    param_grid=param_grid,
    scoring="f1_weighted",
    cv=cv,
    n_jobs=-1,
    verbose=1,
    refit=True,
    return_train_score=True
)

print("\nEjecutando GridSearchCV para Random Forest...")
grid.fit(X_train_vecs, y_train)

print("\n===== MEJOR CONFIGURACIÓN ENCONTRADA =====")
print("Best params :", grid.best_params_)
print(f"Best CV F1  : {grid.best_score_:.4f}")

# ---- Evaluación del mejor modelo sobre TEST ----
best = grid.best_estimator_
y_pred_best  = best.predict(X_test_vecs)
y_proba_best = best.predict_proba(X_test_vecs)

print("\n===== MÉTRICAS DEL MEJOR MODELO (TEST) =====")
print(f"Accuracy           : {accuracy_score(y_test, y_pred_best):.4f}")
print(f"Precision (weighted): {precision_score(y_test, y_pred_best, average='weighted', zero_division=0):.4f}")
print(f"Recall    (weighted): {recall_score(y_test, y_pred_best, average='weighted', zero_division=0):.4f}")
print(f"F1        (weighted): {f1_score(y_test, y_pred_best, average='weighted', zero_division=0):.4f}")
print("\nReporte por clase:")
print(classification_report(y_test, y_pred_best, zero_division=0))

# Matriz de confusión del mejor modelo
cm_best = confusion_matrix(y_test, y_pred_best, labels=LABELS)
fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay(cm_best, display_labels=LABELS).plot(
    cmap="Greens", ax=ax, colorbar=False
)
plt.title("Matriz de Confusión — Random Forest (mejor configuración)")
plt.show()

# ROC del mejor modelo
y_bin_best = label_binarize(y_test, classes=best.classes_)
fig, ax = plt.subplots(figsize=(8, 6))
for i, cls in enumerate(best.classes_):
    fpr, tpr, _ = roc_curve(y_bin_best[:, i], y_proba_best[:, i])
    ax.plot(fpr, tpr, lw=2, label=f"{cls} (AUC={auc(fpr, tpr):.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=1)
ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
ax.set_title("Curvas ROC OvR — Random Forest (mejor configuración)")
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()


# =========================================================
# 7. COMPARATIVA INICIAL vs HIPERPARAMETRIZADO
# =========================================================
def resumen(y_true, y_pred, tag):
    return {
        "Modelo": tag,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision (w)": precision_score(y_true, y_pred, average="weighted", zero_division=0),
        "Recall (w)":    recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "F1 (w)":        f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }

comparativa = pd.DataFrame([
    resumen(y_test, y_pred,      "Random Forest inicial"),
    resumen(y_test, y_pred_best, f"RF tuneado {grid.best_params_}"),
])
print("\n===== COMPARATIVA =====")
print(comparativa.round(4).to_string(index=False))

# Tabla de los 10 mejores resultados del GridSearch
resultados = pd.DataFrame(grid.cv_results_).sort_values("rank_test_score").head(10)
print("\nTop 10 combinaciones según F1 (weighted, CV):")
print(resultados[["params", "mean_test_score", "std_test_score"]].to_string(index=False))

# ---- Conclusión programática ----
mejora = comparativa.iloc[1]["F1 (w)"] - comparativa.iloc[0]["F1 (w)"]
if mejora > 0.005:
    print(f"\n➡️  La hiperparametrización SÍ mejoró el F1 en {mejora:.4f}. "
          f"Configuración óptima: {grid.best_params_}")
else:
    print("\n➡️  La hiperparametrización NO aportó una mejora significativa "
          "(ΔF1 ≤ 0.005). La configuración inicial ya es cercana a la óptima.")
