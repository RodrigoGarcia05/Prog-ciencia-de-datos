mapa_marcadores = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

for _, fila in tampiMadero.iterrows():
    folium.Marker(
        location=[fila['latitud'], fila['longitud']],
        popup=f"<b>{fila['usuario']}</b><br>{fila['textoTweet']}<br><small>{fila['fechaHora']}</small>",
        tooltip=fila['usuario'],
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(mapa_marcadores)

mapa_marcadores
