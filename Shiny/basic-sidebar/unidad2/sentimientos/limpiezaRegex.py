import re

def clean_text(text):
    text = str(text).lower() 
    text = re.sub(r'http\S+', '', text)
    regex = r'[\!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]'
    text = re.sub(regex, '', text)
    
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text) 
    text = re.sub(r'#[A-Za-z0-9_]+', '', text) 
    text = re.sub(r'[^a-zA-Z\s]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip() 
    return text

dGates['Clean_Content'] = dGates['text'].apply(clean_text)
dGates = dGates[dGates['Clean_Content'] != ''].copy() 

dMusk['Clean_Content'] = dMusk['text'].apply(clean_text)
dMusk = dMusk[dMusk['Clean_Content'] != ''].copy()

dLee['Clean_Content'] = dLee['text'].apply(clean_text)
dLee = dLee[dLee['Clean_Content'] != ''].copy()


print("Bill Gates")
display(dGates[['text', 'Clean_Content']].head())
