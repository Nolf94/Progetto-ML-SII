import json
from urllib.request import urlopen

import requests

from Clustering.Clustering import clusterize, summarize
from Doc2Vec.doc2vec_films_vectors import create_vector
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping

from .lod_extractor import (MEDIA_TYPES, get_wikidata_items_from_coordinates,
                            get_wikipedia_abstract_from_querystring,
                            get_wikipedia_abstract_from_wikidata_item)


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

        # for testing purposes only
        # media = ['Full Metal Jacket', 'Avatar', 'Shutter Island', 'Fast & Furious']
        # media = ['Full Metal Jacket']
        
        abstracts = []
        print(f'Retrieving abstracts for {len(media)} {media_type}:')
        for i, element in enumerate(media):
            # TODO improve query performance (or make it non-blocking)
            abstract = get_wikipedia_abstract_from_querystring(element, media_type, i+1)
            if abstract:
                abstracts.append(normalize_text(stopping(abstract)))
        print(f'Retrieved {len(abstracts)} abstracts (number of non-{media_type} elements: {len(media)-len(abstracts)}).')

        vectors = []
        for abstract in abstracts:
            vectors.append(create_vector(abstract))
        return vectors


    def get_items_from_coordinates(self, latitude, longitude, radius, media_type):
        try:
            items = get_wikidata_items_from_coordinates(latitude, longitude, radius, media_type)
            print(f'Retrieving abstracts for {len(items)} {media_type}:')
            for i, item in enumerate(items):
                abstract = get_wikipedia_abstract_from_wikidata_item(item, i+1)
                if not abstract:
                    continue
                item['abstract'] = abstract
                item['vector'] = create_vector(abstract)
            initial_len = len(items)
            items = list(filter(lambda item: 'abstract' in item.keys(), items))
            print(f'Retrieved {len(items)} abstracts (number of non-{media_type} elements: {initial_len-len(items)}).')
            return items
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return


    def build_clustering_model(self, vector_list, eps):
        return clusterize(vector_list, eps)
    
    def build_summarize_model(self, vector_list):
        return summarize(vector_list)
