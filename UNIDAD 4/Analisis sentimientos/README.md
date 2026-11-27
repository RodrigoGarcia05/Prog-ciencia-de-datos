# Análisis de sentimiento – Tweets Tampico / Madero

```
Analisis_Sentimiento_Tampico/
├── analisis_sentimiento_tweets.py      ← script principal
├── requirements.txt
├── datos/
│   └── tweets_tampico_madero_powerbi.csv
└── resultados/                         ← se llena al ejecutar el script
    ├── tweets_sentimiento_powerbi.csv  ← archivo para Power BI
    └── graficas/*.png
```

## Cómo ejecutarlo (Mac, terminal de VS Code)

```bash
cd "Analisis_Sentimiento_Tampico"
# (con tu .venv activado, como ya lo tienes en VS Code)
pip install -r requirements.txt
python3 analisis_sentimiento_tweets.py
```

- En Mac el comando es `python3`, no `python`.
- Si aparece `CERTIFICATE_VERIFY_FAILED`, ejecuta una vez
  `open "/Applications/Python 3.13/Install Certificates.command"` (ajusta la versión) y vuelve a correrlo.
- La traducción al inglés necesita internet. Si Google no responde en 15 s, ese tweet se analiza en español.
- Desde la terminal, las gráficas se guardan como PNG en `resultados/graficas/` (no se abren ventanas).
