# =========================================================
# 5. TF-IDF + SVM  (clasificación del sentimiento)
# =========================================================
X_text = df["texto_limpio"].fillna("")
y = df["sentimiento"]

# Split estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X_text, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")
print("Clases:", sorted(y.unique()))

# Pipeline: TF-IDF -> SVM
pipe_svm = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9,
        sublinear_tf=True
    )),
    ("svm", SVC(
        kernel="linear",
        C=1.0,
        probability=True,          # necesario para ROC
        class_weight="balanced",   # clases desbalanceadas
        random_state=42
    ))
])

pipe_svm.fit(X_train, y_train)

# ---- Predicciones ----
y_pred  = pipe_svm.predict(X_test)
y_proba = pipe_svm.predict_proba(X_test)

# ---- Métricas ----
print("\n===== MÉTRICAS SVM (configuración inicial) =====")
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
plt.title("Matriz de Confusión — SVM (TF-IDF)")
plt.show()

# ---- Curva ROC (One-vs-Rest, multiclase) ----
classes   = pipe_svm.classes_
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
ax.set_title("Curvas ROC One-vs-Rest — SVM (TF-IDF)")
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
# Buscamos sobre:
#  - kernel: linear / rbf
#  - C
#  - gamma (solo rbf)
#  - max_features de TF-IDF
#  - ngram_range
param_grid = [
    # Kernels lineales
    {
        "tfidf__max_features": [None, 20000],
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "svm__kernel": ["linear"],
        "svm__C": [0.1, 1, 10],
    },
    # Kernels RBF
    {
        "tfidf__max_features": [None, 20000],
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "svm__kernel": ["rbf"],
        "svm__C": [0.1, 1, 10],
        "svm__gamma": ["scale", 0.01],
    },
]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    estimator=pipe_svm,
    param_grid=param_grid,
    scoring="f1_weighted",
    cv=cv,
    n_jobs=-1,
    verbose=1,
    refit=True,
    return_train_score=True
)

print("\nEjecutando GridSearchCV...")
grid.fit(X_train, y_train)

print("\n===== MEJOR CONFIGURACIÓN ENCONTRADA =====")
print("Best params :", grid.best_params_)
print(f"Best CV F1  : {grid.best_score_:.4f}")

# ---- Evaluación del mejor modelo sobre TEST ----
best = grid.best_estimator_
y_pred_best  = best.predict(X_test)
y_proba_best = best.predict_proba(X_test)

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
plt.title("Matriz de Confusión — SVM (mejor configuración)")
plt.show()

# ROC del mejor modelo
y_bin_best = label_binarize(y_test, classes=best.classes_)
fig, ax = plt.subplots(figsize=(8, 6))
for i, cls in enumerate(best.classes_):
    fpr, tpr, _ = roc_curve(y_bin_best[:, i], y_proba_best[:, i])
    ax.plot(fpr, tpr, lw=2, label=f"{cls} (AUC={auc(fpr, tpr):.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=1)
ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
ax.set_title("Curvas ROC OvR — SVM (mejor configuración)")
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()


# =========================================================
# 7. COMPARATIVA INICIAL vs HIPERPARAMETRIZADO
# =========================================================
def resumen(y_true, y_pred, tag):
    return {
        "Modelo": tag,
        "Accuracy":  accuracy_score(y_true, y_pred),
        "Precision (w)": precision_score(y_true, y_pred, average="weighted", zero_division=0),
        "Recall (w)":    recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "F1 (w)":        f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }

comparativa = pd.DataFrame([
    resumen(y_test, y_pred,      "SVM inicial (linear, C=1)"),
    resumen(y_test, y_pred_best, f"SVM tuneado {grid.best_params_}"),
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
