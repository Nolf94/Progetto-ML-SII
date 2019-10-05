from gensim.models.doc2vec import Doc2Vec, TaggedLineDocument
#from nltk.tokenize import word_tokenize


#Dati di esempio:
#data = ["I love machine learning. Its awesome.",
#        "I love coding in python",
#        "I love building chatbots",
#        "they chat amagingly well"]



#tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(data)]


#Per funzionare Doc2Vec accetta solamente TaggedDocument:
#A single document, made up of `words` (a list of unicode string tokens)
# and `tags` (a list of tokens). Tags may be one or more unicode string
# tokens, but typical practice (which will also be most memory-efficient) is
# for the tags list to include a unique integer id as the only tag.

tagged_data = TaggedLineDocument("movie.metadata.tsv")

max_epochs = 10
vec_size = 20
alpha = 0.025

model = Doc2Vec(size=vec_size,
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=1)

model.build_vocab(tagged_data)

model.train(tagged_data, total_examples = model.corpus_count, epochs=max_epochs)
model.save('doc2vec.model')

#for epoch in range(max_epochs):
#    print('iteration {0}'.format(epoch))
#    model.train(tagged_data,
#                total_examples=model.corpus_count,
#                epochs=model.iter)
    # decrease the learning rate
#    model.alpha -= 0.0002
    # fix the learning rate, no decay
#    model.min_alpha = model.alpha
#model.save("d2v.model")
print("Model Saved")