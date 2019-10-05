from gensim.models.doc2vec import Doc2Vec
from scipy import spatial


d2v_model = Doc2Vec.load('doc2vec.model')

#Due stringhe di esempio prese dal dataset usato per creare il modello, utilizzate solo per prova
string1 = '14494806	/m/03d57tv	A Boy Named Sue	2000		58.0	{"/m/02h40lc": "English Language"}	{"/m/09c7w0": "United States of America"}	{"/m/0hj3n4b": "Gender Issues", "/m/0hn10": "LGBT", "/m/0hj3n07": "Culture & Society", "/m/017fp": "Biography", "/m/0jtdp": "Documentary"}'
string2 = '1588008	/m/05dpjl	Heidi Fleiss: Hollywood Madam	1995-12-27		106.0	{"/m/02h40lc": "English Language"}	{"/m/09c7w0": "United States of America", "/m/0d060g": "Canada", "/m/07ssc": "United Kingdom", "/m/0345h": "Germany"}	{"/m/017fp": "Biography", "/m/03mqtr": "Political drama", "/m/01z4y": "Comedy"}'

#Confronto tra due documenti ipoteticamente non contenuti nel modello:
vec1 = d2v_model.infer_vector(string1.split())
vec2 = d2v_model.infer_vector(string2.split())

print(string1)
print(string2)

#calcolo della cosine similarity
similarity = spatial.distance.cosine(vec1, vec2)
print(similarity)

#Per confrontare un documento con uno contenuto nel modello (trovare il più simile):

#token = "words associated with my research questions".split()
#new_vector = model.infer_vector(token)
#sims = model.docvecs.most_similar([new_vector])