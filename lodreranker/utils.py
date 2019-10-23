import json
import random
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen
import numpy as np
from django.contrib.staticfiles import finders
from lodreranker.misc import retrieveFilmAbstract
from Doc2Vec.doc2vec_preprocessing import *
from Doc2Vec.doc2vec_films_vectors import *


def get_choices(path='poi'):
    data = open(finders.find(f"js/{path}.json")).read()
    json_data = json.loads(data)
    opts = []

    # json_data = json_data[:3]
    for item in random.sample(json_data, len(json_data)):
    # for item in json_data:
        opts.append(item)
    return opts


def get_poi_weights(selection, choices):
    vectors = []

    for x in selection:
        vectors.append(np.array(choices[int(x)-1]['weights']))
        # print(poi_choices[x-1]['name'])
    # print(vectors)
    # print(sum(vectors))

    weights = sum(vectors)
    return json.dumps(weights.tolist())


def get_wikipedia_abstract(querystring):
    wiki_url = retrieveFilmAbstract(querystring)
    if(wiki_url is not ""):
        wiki_id = re.sub("http://www.wikidata.org/entity/","", wiki_url)
        wikipedia_query = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids=" + wiki_id + "&sitefilter=enwiki"
        wiki_page= json.loads(urlopen(wikipedia_query.rstrip()).read().decode("utf-8"))
        wiki_title = wiki_page["entities"][wiki_id]["sitelinks"]["enwiki"]["title"]
        linkid = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(wiki_title)
        link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" + quote(wiki_title)
        try:
            contents = urlopen(linkid.rstrip()).read()
            pageid = json.loads(contents)
            id = pageid['pageid']
            contents2 = urlopen(link.rstrip()).read()
            extract = json.loads(contents2)
            try:
                abstract = extract['query']['pages'][str(id)]['extract']
                abstract = re.sub('\n', '', abstract)
            except KeyError as keyerror:
                return
                
        except HTTPError as error:
            if error.code == 404:
                return
        return abstract

def get_likes_vectors(extra_data):
    movie_abstracts = []
    for movie in extra_data:
            abstract = get_wikipedia_abstract(movie['name'])
            if(abstract is not None):
                movie_abstracts.append(normalize_text(stopping(abstract)))
    return get_vectors(movie_abstracts)

def get_vectors(movie_abstracts):
    vectors = []
    for abstract in movie_abstracts:
        vectors.append(create_vector(abstract))
    return vectors


  
        
    
        