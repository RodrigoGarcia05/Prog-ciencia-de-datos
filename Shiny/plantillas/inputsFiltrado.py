from shiny.express import ui

# 1. Rango numérico con deslizador doble
ui.input_slider("peso", "Rango de Peso (g):", min=2000, max=8000, value=(3000, 5000))

# 2. Selector de fechas (ideal para series temporales o ventas)
ui.input_date_range("fechas", "Selecciona periodo:", start="2026-01-01")

# 3. Subir archivos personalizados por el usuario (¡Súper útil para Kaggle!)
ui.input_file("archivo_usuario", "Carga tu propio CSV:", accept=[".csv"])
