import os
import re

import nltk
import numpy as np
from gensim.matutils import jaccard
from gensim.models.doc2vec import Doc2Vec
# nltk.download('stopwords') # uncomment if running project for the first time
from nltk.corpus import stopwords

import lodreranker.constants as constants


def normalize_text(text):
    normtext = re.sub(r'[^\w]', ' ', text).lower()
    norm_text = re.sub(' +', ' ', normtext)
    return norm_text


def stopping(text):
    stop_words = set(stopwords.words('english'))
    for word in stop_words:
        text = text.replace(" " + word + " ", " ")
    return text


def create_vector(text, media_type):
    if media_type == constants.MOVIE:
        d2v_model = Doc2Vec.load(os.path.dirname(__file__) + '/doc2vec_data_films.model')
    return d2v_model.infer_vector(normalize_text(stopping(text)).split())

