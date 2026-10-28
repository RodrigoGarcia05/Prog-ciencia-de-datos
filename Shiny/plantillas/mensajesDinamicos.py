# Para dar retroalimentación visual al usuario cuando realiza una acción
# por ejemplo, cuando carga un archivo con éxito o un filtro no arroja resultados

from shiny.express import ui


# Puedes dispararlo dentro de una función reactiva:
def mostrar_alerta():
  ui.notification_show(
      "¡Filtros aplicados correctamente!", type="message", duration=3
  )
