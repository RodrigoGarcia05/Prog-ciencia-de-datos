# Si tu dataset tiene coordenadas (latitud y longitud) o quieres mostrar ubicaciones geográficas, 
# Leaflet es el estándar de oro en Shiny.
# Instala la librería: pip install shinywidgets ipyleaflet

from ipyleaflet import Map, Marker
from shiny.express import render
from shinywidgets import render_widget


@render_widget
def mapa_pinguinos():
  # Centrado en una ubicación de referencia (ej. Tampico o el punto de estudio)
  m = Map(center=(22.233, -97.86), zoom=6)
  m.add_layer(Marker(location=(22.233, -97.86)))
  return m
