# Cuando un dashboard crece y ya no cabe en una sola vista, necesitas organizar 
# el contenido en pestañas (navset_card_tab) o menús desplegables (accordion).

from shiny.express import ui

# Pestañas navegables dentro de una tarjeta
with ui.navset_card_tab():
  with ui.nav_panel("📈 Análisis Principal"):
    ui.p("Aquí va tu gráfica principal de distribución.")

  with ui.nav_panel("📋 Tabla de Datos"):
    ui.p("Aquí puedes poner la tabla interactiva.")

# Acordeón para colapsar y expandir secciones en la barra lateral o cuerpo
with ui.accordion(id="acc"):
  with ui.accordion_panel("Filtros avanzados"):
    ui.input_slider("rango", "Selecciona rango:", 0, 100, 50)
