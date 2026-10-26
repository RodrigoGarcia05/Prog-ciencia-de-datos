from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def tokenizacion(text):
    tokens = word_tokenize(text) 
    return tokens

def preprocess_tokens(text):
    tokens = word_tokenize(text) 
    filtered = [w for w in tokens if w not in stop_words] 
    return " ".join(filtered) 


for df in [dGates, dMusk, dLee]:
    df['texto_tokenizado'] = df['Clean_Content'].apply(tokenizacion)
    df['Final_Content'] = df['Clean_Content'].apply(preprocess_tokens)

print("Bill Gates")
display(dGates[['Clean_Content', 'texto_tokenizado', 'Final_Content']].head())

print("Elon Musk")
display(dMusk[['Clean_Content', 'texto_tokenizado', 'Final_Content']].head())

print("Mayor Ed Lee")
display(dLee[['Clean_Content', 'texto_tokenizado', 'Final_Content']].head())
