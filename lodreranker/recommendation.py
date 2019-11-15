import json
from urllib.request import urlopen

import numpy as np
import requests
from scipy import spatial

from Clustering.clustering import clusterize
from Doc2Vec.doc2vec_films_vectors import create_vector
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping
from lodreranker import constants

from .lod_queries import (retrieve_from_coordinates,
                            get_abstract_from_querystring,
                            get_abstract_from_item)
from .models import RetrievedItem


class ItemRanker(object):
    """Interface for ranking a list of items according to different strategies."""

    def cosine_similarity(self, vec1, vec2):
        """Returns the cosine similarity between vectors vec1 and vec2."""
        return 1 - spatial.distance.cosine(vec1, vec2)

    def rank_items_using_clusters(self, clusters, items):
        """
        Ranks given items using the clustering method.
        Given N clusters, N partial scores are calculated for each item by confrontation with every centroid.
        The ranking is then calculated by summing the partial scores.

        The score of item i according to cluster k is calculated as following:
            score(i,k) = (similarity(i) / total_similarity_k) * weight(k)
        where 
            total_similarity_k = sum(similarity(j,k)) for each item j
        The final score of item i is calculated as following:
            score(i) = sum( score(i,m) ) for each cluster m
        """
        # initialize empty scores
        items = [dict(item, score=0) for item in items]
        for cluster in clusters:
            # calculate similarity between each item and current cluster's centroid
            relative_sims = {}
            for item in items:
                similarity = self.cosine_similarity(cluster["centroid"], item["vector"])
                relative_sims[item['id']] = similarity
            # sum similarities for normalization
            relative_sims_tot = sum(x for x in relative_sims.values())
            # item partial score = normalized similarity * cluster's weight
            for item in items:
                item['score'] += (relative_sims[item['id']]/relative_sims_tot) * cluster['weight']

        ranked_items = sorted(items, reverse=True, key=lambda item: item['score'])
        for i, item in enumerate(ranked_items):
            print(f"{str(i+1)}, {item['score']}, {item['id']}, {item['name']}")
        return ranked_items

    def rank_items_using_sum(self, sum, items):
        """
        Ranks given items using the sum method.
        Given a sum vector, the ranking is obtained by simply calculatig similarity between the vector and each item.
        """
        items = [dict(item, score=self.cosine_similarity(sum, item["vector"])) for item in items]
        ranked_items = sorted(items, reverse=True, key=lambda item: item['score'])
        for i, item in enumerate(ranked_items):
            print(f"{str(i+1)}, {item['score']}, {item['id']}, {item['name']}")
        return ranked_items


class ItemRetriever(object):
    """Interface for retrieving items from Linked Open Data (LOD), such as Wikidata."""
    def __init__(self, media_type, coords=None, max_retrieved_items=None):
        self.mtype = media_type
        self.coords = coords
        self.retrieved_items = []
        self.max_retrieved_items = max_retrieved_items


    def get_items_from_social(self, extra_data_media):
        """Retrieves vectors from social network data."""
        media = extra_data_media['data']
        # if data is split across multiple pages, fetch them all.
        has_next = 'next' in extra_data_media['paging'].keys()
        while has_next:
            next_page = json.loads(urlopen(extra_data_media['paging']['next']).read().decode('utf-8'))
            media.extend(next_page['data'])
            has_next = 'next' in next_page['paging'].keys()
        media = list(map(lambda x: x['name'], media))
                
        abstracts = []
        print(f'Retrieving abstracts for {len(media)} {self.mtype}:')
        for i, querystring in enumerate(media):
            
            try:
                item = RetrievedItem.objects.get(querystring=querystring)
                abstract = item.abstract
            except RetrievedItem.DoesNotExist:
                item = get_abstract_from_querystring(querystring, self.mtype, i+1)
            abstract = item.abstract
            
            if abstract:                
                abstracts.append(normalize_text(stopping(abstract)))
        print(f'Retrieved {len(abstracts)} abstracts (number of non-{self.mtype} elements: {len(media)-len(abstracts)}).')

        vectors = []
        for abstract in abstracts:
            vectors.append(create_vector(abstract))
        return vectors


    def get_items_from_coordinates(self):
        try:
            items = retrieve_from_coordinates(self.coords, self.mtype)
            print(f'Retrieving abstracts for {len(items)} {self.mtype}:')
            for i, item in enumerate(items):
                abstract = get_abstract_from_item(item, i+1)
                if not abstract:
                    continue
                item.abstract = abstract
                item.vector = create_vector(abstract)
            initial_len = len(items)
            items = list(filter(lambda item: 'abstract' in item.keys(), items))
            print(f'Retrieved {len(items)} abstracts (number of non-{self.mtype} elements: {initial_len-len(items)}).')
            return items
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return


class Recommender(object):
    """Main interface for recommendation."""
    def __init__(self, user, media_type, coords, max_retrieved_items=50):
        self.user = user
        self.mtype = media_type
        self.retriever = ItemRetriever(self.mtype, coords, max_retrieved_items)
        self.vectors = json.loads(eval(f'user.form_{media_type}'))
        for vec in json.loads(eval(f'user.social_{self.mtype}')):
            if vec not in self.vectors:
                self.vectors.append(vec)

    def recommend(self, media_type, method):
        if method == 'clustering':
            print('Using clustering')
            eps = 0.50
            clusters = clusterize(self.vectors, eps)
            print(f'Vectors: {len(self.vectors)}, Clusters: {len(clusters)}') 
            for cluster in clusters:
                print(cluster['weight'])

            items = self.retriever.retrieved_items
            return ItemRanker().rank_items_using_clusters(clusters, items)
        
        elif method == 'summarize':
            print('Using summarize')
            items = self.retriever.retrieved_items
            return ItemRanker().rank_items_using_sum(sum(np.array(self.vectors)), items)