# permite que el usuario haga zoom, pase el cursor para ver valores exactos (tooltips) y mueva los ejes de forma interactiva.
# Instala plotly: pip install plotly

import plotly.express as px
from shiny.express import render, ui


@render.ui
def grafico_plotly():
  # Creamos una gráfica interactiva con plotly express
  fig = px.scatter(
      df,
      x="bill_length_mm",
      y="body_mass_g",
      color="species",
      template="plotly_dark",  # Combina perfecto con tu tema oscuro
  )
  return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))
