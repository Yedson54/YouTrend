import re
import nltk
import wordcloud
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Union
import io
import requests
import PIL

def clean_text(text:List) -> str:
    text = text.lower()
    text = " ".join(text.split())
    return text

def get_clean_tokenized_data(data:str, language:str = "french") -> List:
    words = nltk.word_tokenize(data, language=language)
    STOPWORDS = set(nltk.corpus.stopwords.words('french'))
    words = [w for w in words if not w in STOPWORDS and w.isalpha()]
    return words

def get_mask(url_img:str, default_mask:str = "assets/images/cloud.jpeg"):
    response = requests.get(url_img)
    img = io.BytesIO(response.content) if (response.status_code == 200) else default_mask
    return np.array(PIL.Image.open(img))

def gen_wordcloud(corpus:str, max_words:int = 400, mask:Union[np.ndarray, None] = None):
    wc = wordcloud.WordCloud(background_color="white", max_words=max_words, mask=mask, contour_width=3, contour_color="white")
    return wc.generate(corpus)

def plot_wc(wc: wordcloud.WordCloud):
    fig = plt.figure(figsize=(10, 10))

    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
