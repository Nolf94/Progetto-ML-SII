from nltk.tokenize import sent_tokenize, word_tokenize
import warnings

warnings.filterwarnings(action='ignore')

import gensim

sample = open("alice.txt", "r")
s = sample.read()

f = s.replace("\n", " ")

data = []

for i in sent_tokenize(f):
    temp = []

    for j in word_tokenize(i):
        temp.append(j.lower())

    data.append(temp)

modell = gensim.models.Word2Vec(data, min_count = 1, size = 100, window = 5)

print("Cosine similarity between 'alice' and 'wonderland:",
      modell.similarity('alice', 'wonderland'))


# Create Skip Gram model
model2 = gensim.models.Word2Vec(data, min_count=1, size=100,
                                window=5, sg=1)


print(modell["alice"])
print(modell["wonderland"])

print("Cosine similarity between 'alice' " +
      "and 'machines' - Skip Gram : ",
      model2.similarity('alice', 'alice'))

print(model2["alice"])
print(model2["wonderland"])