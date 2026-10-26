from wordcloud import WordCloud
import matplotlib.pyplot as plt

usuarios_textos = {
    "Bill Gates": " ".join(dGates["Final_Content"].astype(str)),
    "Elon Musk": " ".join(dMusk["Final_Content"].astype(str)),
    "Mayor Ed Lee": " ".join(dLee["Final_Content"].astype(str))
}

for usuario, texto_completo in usuarios_textos.items():
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color="white", 
        colormap="plasma"
    ).generate(texto_completo)
    
 
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(f"Word Cloud - {usuario}")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
