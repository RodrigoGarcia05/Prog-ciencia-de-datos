import folium

lat_centro = tampiMadero["latitud"].mean()
lon_centro = tampiMadero["longitud"].mean()

mapa_base = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)
mapa_base
