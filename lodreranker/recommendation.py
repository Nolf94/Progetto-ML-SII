import json
import re
from urllib.request import urlopen

import numpy as np
from scipy import spatial

import Clustering.clustering as clustering
import Doc2Vec.doc2vec as d2v
from lodreranker import constants, lod_queries
from lodreranker import utils
from lodreranker.models import RetrievedItem

class Candidate(object):
    """A Candidate is a RetrievedItem with an additional score used to rank it in a list."""
    def __init__(self, item: RetrievedItem):
        self.item = item
        self.score = 0

class ItemRanker(object):
    """Interface for ranking a list of items according to different strategies."""

    def __init__(self, items):
        # A candidate is a dictionary with two kv pairs:
        #   item (the candidate's details)
        #   score (the candidate's score)
        # self.candidates = [dict(item=item, score=0) for item in items]
        self.candidates = [Candidate(item) for item in items]
        print(f'\t{type(self).__name__} initialized with {len(items)} candidates')

    def __cosine_similarity(self, vec1, vec2):
        """Private method: returns the cosine similarity between vectors vec1 and vec2."""
        return 1 - spatial.distance.cosine(vec1, vec2)

    def __get_ranking(self):
        """Private method: calculates and returns the ranking according to the candidates' scores."""
        ranking = sorted(self.candidates, reverse=True, key=lambda candidate: candidate.score)
        print(f'\t{type(self).__name__} calculated the following ranking:')
        for i, candidate in enumerate(ranking):
            item = candidate.item
            print(f"\t{str(i+1)}) {round(candidate.score, 3)}\t{item.wkd_id}\t({item.name})")
        return ranking

    def rank_items_using_clusters(self, clusters):
        """
        Ranks using the clustering method.
        Given N clusters, N partial scores are calculated for each item by confrontation with every centroid.
        The ranking is then calculated by summing the partial scores.

        The score of item i according to cluster k is calculated as follows:
            score(i,k) = (similarity(i) / total_similarity_k) * weight(k)
        where
            total_similarity_k = sum(similarity(j,k)) for each item j
        The final score of item i is calculated as following:
            score(i) = sum( score(i,m) ) for each cluster m
        """
        for cluster in clusters:
            relative_sims = {}
            for candidate in self.candidates:
                item = candidate.item
                similarity = self.__cosine_similarity(cluster["centroid"], json.loads(item.vector))
                relative_sims[item.wkd_id] = similarity

            relative_sims_tot = sum(x for x in relative_sims.values())
            for candidate in self.candidates:
                candidate.score += (relative_sims[candidate.item.wkd_id]/relative_sims_tot) * cluster['weight']

        return self.__get_ranking()

    def rank_items_using_sum(self, sum_vec):
        """
        Ranks using the sum method.
        Given a sum vector, the ranking is obtained by simply calculatig similarity between the vector and each item.
        """
        for candidate in self.candidates:
            candidate.score = self.__cosine_similarity(sum_vec, json.loads(candidate.item.vector))

        return self.__get_ranking()

    def rank_items_outdegree(self):
        """
        Ranks without any given input:
        The candidates' scores are simply inferred by the items outdegree, which comes from wikidata itself.
        """
        for candidate in self.candidates:
            candidate.score = candidate.item.outdegree

        return self.__get_ranking()


class ItemRetriever(object):
    """Interface for retrieving items from Linked Open Data (LOD), such as Wikidata."""
    def __init__(self, media_type):
        if type(self) is ItemRetriever:
            raise Exception('ItemRetriever is an abstract class and cannot be instantiated directly')
        self.mtype = media_type

    def initialize(self):
        self.retrieved_items = []
        self.current = None
        # self.next = True # we use True instead of None to trigger the first recursive ajax call
        self.next = self.input_set[0] if self.input_set else None
        self.i = 0
        self.tot = len(self.input_set)
        print(f'{type(self).__name__} for {self.mtype} initialized with {self.tot} inputs.')

    def retrieve_next(self):
        self.current = self.input_set.pop(0)
        self.next = self.input_set[0] if self.input_set else None
        self.i += 1
        print(f'[{self.i}/{self.tot}] {self.current}')


class SocialItemRetriever(ItemRetriever):
    def __init__(self, media_type):
        super().__init__(media_type)

    def initialize(self, extra_data_media):
        self.input_set = []
        media = extra_data_media['data']

        def has_next(page):
            return 'next' in page['paging'].keys()

        # if data is split across multiple pages, keep fetching from pages until page limit is reached.
        if has_next(extra_data_media):
            print(f'FB {self.mtype} are on more than one page, fetching (max: {constants.FB_FETCH_PAGE_LIMIT})')
            i=2
            current_page = extra_data_media
            while has_next(current_page) and i <= constants.FB_FETCH_PAGE_LIMIT:
                print(f'FB {self.mtype}: fetching next page ({i})')
                next_page_url = current_page['paging']['next']
                current_page = json.loads(urlopen(next_page_url).read().decode('utf-8'))
                media.extend(current_page['data'])
                i+=1

        if media:
            self.input_set = list(map(lambda x: x['name'], media))
        # self.input_set = self.input_set[:3]
        super().initialize()

    def retrieve_next(self):
        utils.disablePrint()
        super().retrieve_next()
        wkb = lod_queries.Wikibase()
        spql = lod_queries.Sparql(constants.WIKIDATA)

        try: # look for cached item
            item = RetrievedItem.objects.get(querystring=self.current)
            print(f'\t"{self.current}" found cached: {item.wkd_id}.')

        except RetrievedItem.DoesNotExist: # (try to) get new item
            print(f'\t"{self.current}" is new. Searching Wikibase for Entities matching with type "{self.mtype}"...')
            found_matching_entity = False
            search_results = wkb.search(self.current)
            if not search_results:
                print(f'\t"{self.current}": No entities found.')
            for i, entity in enumerate(search_results):
                wkd_id = entity['id']
                desc = entity["description"] if 'description' in entity.keys() else None
                print(f'\t[{i+1}/{len(search_results)}] {entity["label"]} ({desc})')
                query = spql.get_query(self.mtype, 'light', wkd_id)
                try:
                    binding = spql.execute(query)[0]
                    print(f'\t\tEntity type matches with {self.mtype}.')
                    try:
                        item = RetrievedItem.objects.get(wkd_id=wkd_id)
                        print(f'\t"{self.current}" found cached {item.wkd_id}.')
                    except RetrievedItem.DoesNotExist:
                        item = RetrievedItem(
                            wkd_id=re.sub('http://www.wikidata.org/entity/', '', wkd_id),
                            media_type=self.mtype,
                            querystring=self.current,
                            name=entity['label'],
                        )
                        item.save()
                        print(f'\t"{self.current}" returned new item: {item.wkd_id}.')
                    found_matching_entity = True
                    break
                except Exception as e:
                    print(f'\t\t{e}')
            if not found_matching_entity:
                print(f'\t"{self.current}" is invalid. Skipping.. ')
                return # TODO exception handling in AJAX

        if not item.abstract:
            abstract = wkb.retrieve_abstract(item)
            if abstract:
                item.abstract = abstract
                item.vector = json.dumps(d2v.create_vector(abstract, self.mtype).tolist())
                item.save() # update item adding abstract and vector
        if item.vector:
            self.retrieved_items.append(item.wkd_id)
        utils.enablePrint()


class GeoItemRetriever(ItemRetriever):
    def __init__(self, media_type, limit=None):
        self.limit = limit
        super().__init__(media_type)

    def initialize(self, geoarea):
        self.input_set = []
        spql = lod_queries.Sparql(constants.WIKIDATA, limit=self.limit)
        try:
            bindings = spql.execute(spql.get_query(self.mtype, 'geolocalized', geoarea))
            self.input_set = list(map(lambda x: {
                    'id': re.sub('http://www.wikidata.org/entity/', '', x['item']['value']),
                    'name': x['itemLabel']['value'],
                    'outdegree': x['outDegree']['value']
                }, bindings))

            print("\tInitial rank according to wikidata item outDegree:")
            for i, element in enumerate(self.input_set):
                # NB: This rank includes potentially invalid items (which have no abstract)
                print(f"\t{i+1}) {element['outdegree']}\t{element['name']}")
            
        except Exception as e:
            print(f'{type(self).__name__} for {self.mtype}: {e}')
        super().initialize()

    def retrieve_next(self):
        super().retrieve_next()
        try: # use cached item
            item = RetrievedItem.objects.get(wkd_id=self.current['id'])
            print(f'\t\"{self.current["name"]}\" found cached: {item.wkd_id}.')
            
            # (TODO temporary) update existing items with outdegree
            item.outdegree = self.current['outdegree']
            item.save()
            # ------------------------------------------------------

        except RetrievedItem.DoesNotExist: # create new item
            item = RetrievedItem(
                wkd_id=self.current['id'],
                media_type=self.mtype,
                name=self.current['name'],
                outdegree=self.current['outdegree'],
            )
            item.save()

        if not item.abstract:
            abstract = lod_queries.Wikibase().retrieve_abstract(item)
            if abstract:
                item.abstract = abstract
                item.vector = json.dumps(d2v.create_vector(abstract, self.mtype).tolist())
                item.save() # update item adding abstract and vector
        if item.vector:
            self.retrieved_items.append(item.wkd_id)


class Recommender(object):
    """Main interface for recommendation."""
    def __init__(self, media_type, user, retriever: ItemRetriever):
        self.user = user
        self.retriever = retriever

        # form vectors are directly loaded from json
        self.uservectors = json.loads(eval(f'user.form_{media_type}'))

        # social vectors are retrieved from associated RetrievedItems
        for item in self.user.social_items.all():
            if item.media_type == media_type and item.vector:
                vector = json.loads(item.vector)
                if vector not in self.uservectors:
                    self.uservectors.append(vector)
        self.uservectors = np.array(self.uservectors)

    def recommend(self, method='summarize'):
        utils.disablePrint()
        """Before calling this function, be sure that the recommender's retriever has retrieved items."""
        itemids = self.retriever.retrieved_items
        if not itemids:
            raise utils.RetrievalError
        items = [RetrievedItem.objects.get(wkd_id=itemid) for itemid in itemids]
        print(f'{type(self).__name__}: recommending using method "{method}"')
        ranker = ItemRanker(items)
        if method == 'clustering':
            eps = 0.50
            clusters = clustering.clusterize(self.uservectors, eps)
            print(f'{type(self).__name__}: starting clustering. Vectors: {len(self.uservectors)}, Clusters: {len(clusters)}')
            for i, cluster in enumerate(clusters):
                print(f"\tcluster {i+1} - weight: {cluster['weight']}")

            ranking = ranker.rank_items_using_clusters(clusters)

        elif method == 'summarize':
            sum_vec = sum(np.array(self.uservectors))
            ranking = ranker.rank_items_using_sum(sum_vec)

        elif method == 'outdegree':
            ranking = ranker.rank_items_outdegree()

        utils.enablePrint()
        return ranking
