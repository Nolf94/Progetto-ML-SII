from gensim.models import Doc2Vec
from sklearn.cluster import DBSCAN
import numpy as np

model = Doc2Vec.load('../Doc2Vec/doc2vec_data_films.model')

docs = open("docs.txt", "r")

for doc in docs:
    print(doc)
    doc_vecs = model.infer_vector(doc.split())
    print(doc_vecs)
# creating a matrix from list of vectors
    doc_vec = np.reshape(doc_vecs, (-1 , 1))
    mat = np.stack(doc_vec)

# Clustering DBScan
dbscan_model = DBSCAN(metric='cosine')
#Performs clustering on X and returns cluster labels.
labels = dbscan_model.fit_predict(mat)

print(labels)