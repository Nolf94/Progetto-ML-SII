from gensim.models.doc2vec import TaggedLineDocument
from gensim.models import Doc2Vec
import os
import gensim.models.doc2vec
import multiprocessing
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping


# Per funzionare Doc2Vec accetta solamente TaggedDocument:
# A single document, made up of `words` (a list of unicode string tokens)
# and `tags` (a list of tokens). Tags may be one or more unicode string
# tokens, but typical practice (which will also be most memory-efficient) is
# for the tags list to include a unique integer id as the only tag.

# TaggedLineDocument: Iterate over a file that contains documents: one line = TaggedDocument object.

os.system("rm -r doc2vec_data_artists.model")
os.system("rm -r data_artists_result.txt")

cores = multiprocessing.cpu_count()
f = open("data_artist.txt", encoding="utf8")
with open("data_artist_result.txt", 'a', encoding="utf8") as file:
    for line in f:
        line = normalize_text(stopping(line))
        file.write(line + "\n")

tagged_data = TaggedLineDocument("data_artist_result.txt")

assert gensim.models.doc2vec.FAST_VERSION > -1, "This will be painfully slow otherwise"
model = Doc2Vec(dm=1, vector_size=100, window=5, hs=0, min_count=2, sample=0,
                epochs=20, workers=cores)

model.build_vocab(tagged_data)

model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
model.save('doc2vec_data_artist.model')


