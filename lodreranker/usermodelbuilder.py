import json
from urllib.request import urlopen

import requests

from Doc2Vec.doc2vec_films_vectors import create_vector
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping
from Clustering.Clustering import clusterize

from .lod_extractor import MEDIA_TYPES
from .lod_extractor import get_wikipedia_abstract

class UserModelBuilder(object):

    def get_vectors_from_social(self, extra_data_media, media_type):
        if media_type not in MEDIA_TYPES:
            print('Error: bad media type')
            return

        media = extra_data_media['data']
        # if data is split across multiple pages, fetch them all.
        has_next = 'next' in extra_data_media['paging'].keys()
        while has_next:
            next_page = json.loads(urlopen(extra_data_media['paging']['next']).read().decode('utf-8'))
            media.extend(next_page['data'])
            has_next = 'next' in next_page['paging'].keys()
        media = list(map(lambda x: x['name'], media))

        #for testing purposes only
        # media = ['Full Metal Jacket', 'Avatar', 'Shutter Island', 'Fast & Furious']
        media = ['Full Metal Jacket']
        
        abstracts = []
        print(f'Retrieving abstracts for {len(media)} {media_type}:')
        for element in media:
            # TODO improve query performance (or make it non-blocking)
            abstract = get_wikipedia_abstract(element, media_type)
            if abstract:
                abstracts.append(normalize_text(stopping(abstract)))
        print(f'Retrieved {len(abstracts)} abstracts (number of non-{media_type} elements: {len(media)-len(abstracts)}).')

        vectors = []
        for abstract in abstracts:
            vectors.append(create_vector(abstract))
        return vectors


    def build_model(self, vector_list):
        return clusterize(vector_list)
