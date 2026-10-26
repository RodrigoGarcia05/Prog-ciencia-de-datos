from folium.plugins import HeatMap

mapa_calor = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

coordenadas = tampiMadero[['latitud', 'longitud']].values.tolist()

HeatMap(coordenadas).add_to(mapa_calor)

mapa_calor
