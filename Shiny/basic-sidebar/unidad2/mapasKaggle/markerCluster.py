from folium.plugins import MarkerCluster

mapa_agrupado = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)
cluster = MarkerCluster().add_to(mapa_agrupado)

for _, fila in tampiMadero.iterrows():
    folium.Marker(
        location=[fila['latitud'], fila['longitud']],
        popup=fila['textoTweet'],
        tooltip=fila['usuario']
    ).add_to(cluster)

mapa_agrupado
