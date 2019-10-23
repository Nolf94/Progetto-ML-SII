from gensim.models.doc2vec import Doc2Vec
from scipy import spatial
from gensim.matutils import jaccard
import numpy as np
import os

def create_vector(abstract):
    d2v_model = Doc2Vec.load(os.path.dirname(__file__) + '/doc2vec_data_films.model')
    vector = d2v_model.infer_vector(abstract.split())
    return vector
    