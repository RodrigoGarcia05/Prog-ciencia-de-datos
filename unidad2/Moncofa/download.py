import numpy as np
import pandas as pd
from MakeSens import MakeSens

fecha_inicio = "2024-01-01 00:00:00"
fecha_fin = "2024-08-30 00:00:00"
estacion = "mE1_00012"
frecuencia = "1H"

data = MakeSens.download_data(estacion, fecha_inicio, fecha_fin, frecuencia)
data_export = data.reset_index()

data_export.to_csv("datos_estacion_mE1_00012.csv", index=False)

print("Archivo CSV generado")
data.head()
