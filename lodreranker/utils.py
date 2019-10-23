import json
import random
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np
from django.contrib.staticfiles import finders

from Doc2Vec.doc2vec_films_vectors import create_vector
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping
from lodreranker.misc import retrieveFilmAbstract


def get_choices(path='poi'):
    data = open(finders.find(f'js/{path}.json')).read()
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
    try:
        print(f'Retrieving abstract for querystring: "{querystring}"...')
        wiki_url = retrieveFilmAbstract(querystring)
        if wiki_url:
            wkd_id = re.sub('http://www.wikidata.org/entity/','', wiki_url)
            print(f'\tQuerystring "{querystring}" returned wikidata item: {wkd_id}.')
            wkd_query = f'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids={wkd_id}&sitefilter=enwiki'
            wkd_item = json.loads(urlopen(wkd_query.rstrip()).read().decode('utf-8'))
            wiki_page_title = wkd_item['entities'][wkd_id]['sitelinks']['enwiki']['title']
            print(f'\tFound wikipedia page with title: {wiki_page_title}.')
        
            # We use the old wikipedia API because the following query:
            #   https://en.wikipedia.org/api/rest_v1/page/summary/{quote(wiki_title)}
            # returns just the first paragraph of the summary. We need the whole block instead.

            # Parameters:
            # exintro -> return only the content before the first section (our abstract)
            # explaintext -> extract plain text instead of HTML
            # indexpageids -> include additional page ids section listing all returned page IDS (useful since we don't want to know the page ID).

            wiki_extracts_query = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&indexpageids&redirects=1&titles=' \
                + quote(wiki_page_title)
            print(f'\tFetching abstract...')
            response = json.loads(urlopen(wiki_extracts_query.rstrip()).read())['query']
            wiki_page_id = response['pageids'][0]
            abstract = response['pages'][str(wiki_page_id)]['extract']
            
            return re.sub('\n', '', abstract)

    except HTTPError as error:
        if error.code == 404:
            return
    except KeyError as e:
        print(f'\tKeyerror: {str(e)}')
        return
    except Exception as e:
        print(str(e))
        return


def get_likes_vectors(extra_data):
    movie_abstracts = []
    for movie in extra_data:
        abstract = get_wikipedia_abstract(movie['name'])
        if abstract:
            movie_abstracts.append(normalize_text(stopping(abstract)))

    vectors = []
    for abstract in movie_abstracts:
        vectors.append(create_vector(abstract))
    return vectors
