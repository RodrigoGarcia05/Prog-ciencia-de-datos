# tablas con paginación, filtros y ordenamiento automático mediante DataGrid.

from shiny.express import render
from shared import df  # Tu dataframe


# Tabla interactiva moderna
@render.data_frame
def tabla_datos():
  return render.DataGrid(df, selection_mode="row")
