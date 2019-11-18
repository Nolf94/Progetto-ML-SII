import json
import re
from urllib.request import urlopen

import numpy as np
from scipy import spatial

import Clustering.clustering as clustering
import Doc2Vec.doc2vec as d2v
from lodreranker import constants, lod_queries, models


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
    def __init__(self, media_type):
        self.mtype = media_type


class SocialItemRetriever(ItemRetriever):
    def __init__(self, media_type):
        super().__init__(media_type)

    def initialize(self, extra_data_media):
        # if data is split across multiple pages, fetches from all pages.
        media = extra_data_media['data']
        has_next = 'next' in extra_data_media['paging'].keys()
        while has_next:
            next_page = json.loads(urlopen(extra_data_media['paging']['next']).read().decode('utf-8'))
            media.extend(next_page['data'])
            has_next = 'next' in next_page['paging'].keys()

        self.retrieved_items = []
        self.qss = list(map(lambda x: x['name'], media))
        self.current = None
        self.next = True # we use True instead of None to trigger the first recursive ajax call
        self.i = 0
        self.tot = len(self.qss)

    def retrieve_next(self):
        self.current = self.qss.pop(0)
        self.next = self.qss[0] if self.qss else None
        self.i += 1
        print(f'[{self.i+1}/{len(self.qss)}] "{self.current}"')
        try: # use cached item
            item = models.RetrievedItem.objects.get(querystring=self.current)
            print(f'\t"{self.current}" found cached: {item.wkd_id}.')
        except models.RetrievedItem.DoesNotExist: # (try to) get new item
            sm = lod_queries.Sparql()
            if self.mtype == constants.MOVIE:
                query = sm.get_query_movies_querystring(self.current)

            try:
                binding = sm.execute(query)[0]
            except Exception as e:
                print(f'\t"{self.current}": {e}')
                return # TODO exception handling

            item = models.RetrievedItem(
                wkd_id=re.sub('http://www.wikidata.org/entity/', '', binding['item']['value']),
                media_type=self.mtype,
                querystring=self.current,
                name=binding['itemLabel']['value'],
            )
            item.save()
            print(f'\t"{self.current}" returned new item: {item.wkd_id}.')

        if not item.abstract:
            abstract = lod_queries.Wiki().retrieve_abstract(item)
            if abstract:
                item.abstract = abstract
                item.vector = json.dumps(d2v.create_vector(abstract, self.mtype).tolist())
                item.save() # update item adding abstract and vector
        if item.vector:
            self.retrieved_items.append(item.wkd_id)

    """ BULK LOAD UNUSED"""
    # def retrieve_from_social(self, extra_data_media):
        # """Retrieves items from social network data."""

        # # if data is split across multiple pages, fetches from all pages.
        # media = extra_data_media['data']
        # has_next = 'next' in extra_data_media['paging'].keys()
        # while has_next:
        #     next_page = json.loads(urlopen(extra_data_media['paging']['next']).read().decode('utf-8'))
        #     media.extend(next_page['data'])
        #     has_next = 'next' in next_page['paging'].keys()

        # # BULK PROCESS
        # valid_items = []
        # # qss is a list of querystrings, aka names which MIGHT represent a linked open data item.
        # qss = list(map(lambda x: x['name'], media))
        # print(f'Starting retrieval for {self.mtype} from {len(qss)} querystrings:')
        # for i, qs in enumerate(qss):
        #     print(f'[{i+1}/{len(qss)}] "{qs}"')
        #     try: # use cached item
        #         item = models.RetrievedItem.objects.get(querystring=qs)
        #         print(f'\t"{qs}" found cached: {item.wkd_id}.')
        #     except models.RetrievedItem.DoesNotExist: # (try to) get new item
        #         sm = lod_queries.Sparql()
        #         if self.mtype == constants.MOVIE:
        #             query = sm.get_query_movies_querystring(qs)

        #         try:
        #             binding = sm.execute(query)[0]
        #         except Exception as e:
        #             print(f'\t"{qs}": {e}')
        #             continue

        #         item = models.RetrievedItem(
        #             wkd_id=re.sub('http://www.wikidata.org/entity/', '', binding['item']['value']),
        #             media_type=self.mtype,
        #             querystring=qs,
        #             name=binding['itemLabel']['value'],
        #         )
        #         item.save()
        #         print(f'\t"{qs}" returned new item: {item.wkd_id}.')

        #     if not item.abstract:
        #         abstract = lod_queries.Wiki().retrieve_abstract(item)
        #         if abstract:
        #             item.abstract = abstract
        #             item.vector = json.dumps(d2v.create_vector(abstract, self.mtype).tolist())
        #             item.save() # update item adding abstract and vector
        #     if item.vector:
        #         valid_items.append(item)
        # print(f'Retrieved {len(valid_items)} valid items from {len(qss)} querystrings ' +
        #     f'({len(qss)-len(valid_items)} invalid querystrings or items).')
        # return valid_items


class GeoItemRetriever(ItemRetriever):
    def __init__(self, media_type, max_to_retrieve=50):
        super().__init__(media_type)
        self.max_to_retrieve = max_to_retrieve

    def retrieve_from_geoarea(self, geoarea):
        """Retrieves items from geoarea."""

        # BULK PROCESS
        valid_items = []
        print(f'Starting retrieval for {self.mtype} in geoarea {geoarea}:')
        # geo_items is a list of linked open data items which might be valid (have a wiki page in the selected language).
        geo_items=[]
        sm = lod_queries.Sparql()
        if self.mtype == constants.MOVIE:
            query = sm.get_query_movies_geolocalized(geoarea)

        try:
            bindings = sm.execute(query)
        except Exception as e:
            print(e)
            return valid_items

        for binding in bindings:
            wkd_id = re.sub('http://www.wikidata.org/entity/', '', binding['item']['value'])
            try: # use cached item
                item = models.RetrievedItem.objects.get(wkd_id=wkd_id)
                print(f'Found cached item: {item.wkd_id}')
            except models.RetrievedItem.DoesNotExist: # create new item
                item = models.RetrievedItem(
                    wkd_id=wkd_id,
                    media_type=self.mtype,
                    name=binding['itemLabel']['value'],
                )
                item.save()
                print(f'Found new item: {item.wkd_id}')
            geo_items.append(item)

        for i, item in enumerate(geo_items):
            print(f'[{i+1}/{len(geo_items)}] "{item.name}"')
            if not item.abstract:
                abstract = lod_queries.Wiki().retrieve_abstract(item)
                if abstract:
                    item.abstract = abstract
                    item.vector = json.dumps(d2v.create_vector(abstract, self.mtype).tolist())
                    item.save() # update item adding abstract and vector
            if item.vector:
                valid_items.append(item)

        print(f'Retrieved {len(valid_items)} valid items.')
        return valid_items


class Recommender(object):
    """Main interface for recommendation."""
    def __init__(self, user, media_type, max_to_retrieve=None):
        self.user = user
        self.mtype = media_type
        self.retriever = GeoItemRetriever(self.mtype, max_to_retrieve)

        # form vectors are directly loaded from json
        self.uservectors = json.loads(eval(f'user.form_{media_type}'))

        # social vectors are retrieved from associated RetrievedItems
        for item in self.user.social_items.all():
            if item.vector and item.vector not in self.uservectors:
                self.uservectors.append(json.loads(item.vector))
        self.uservectors = np.array(self.uservectors)

    def recommend(self, media_type, method='summarize'):
        if method == 'clustering':
            eps = 0.50
            clusters = clustering.clusterize(self.uservectors, eps)
            print(f'Vectors: {len(self.uservectors)}, Clusters: {len(clusters)}')
            for i, cluster in enumerate(clusters):
                print(f"{i+1} - weight: {cluster['weight']}")

            # ----------------------------------- #
            items = self.retriever.retrieved_items
            # ----------------------------------- #

            return ItemRanker().rank_items_using_clusters(clusters, items)

        elif method == 'summarize':
            items = self.retriever.retrieved_items
            return ItemRanker().rank_items_using_sum(sum(np.array(self.uservectors)), items)
