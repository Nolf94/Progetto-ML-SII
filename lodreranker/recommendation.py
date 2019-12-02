import json
import re
from urllib.request import urlopen

import numpy as np
from scipy import spatial

from Clustering.clustering import Clusterer
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

    def __init__(self, items, strip=False):
        """
        Parameters:
        - items: a list of RetrievedItems
        - strip: if true, the ranker will return just the ranked item's id and score.
        """
        self.candidates = [Candidate(item) for item in items]
        self.strip = strip
        print(f'\t{type(self).__name__} initialized with {len(items)} candidates, will strip: {self.strip}')

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

        if self.strip:
            # strip the ranking from all info but the candidate's item id and score
            ranking = [dict(id=candidate.item.wkd_id, score=round(candidate.score, 3)) for candidate in ranking]
        return ranking

    def rank_items_using_clusters(self, clusters):
        """
        Ranks using the clustering method.
        Given N items and M clusters:
        - For each cluster k, N similarities relative to that cluster are calculated as follows:
            relative_sims(k) = [cossim(i1,k), cossim(i2,k), ..., cossim(iN, k)] 
        - The similarities are then normalized by mapping from range [-1,1] to range [0,1], with the formula:
            x' = (x-min(relative_sims(k))/(max(relative_sims(k)-min(relative_sims(k))))
            so that the item with the highest similarity has similarity=1,
            and the item with the lowest has similarity=0

        - Each similarity is then multiplied for the cluster's weight, making it a partial score for item i:
            partial_score(i,k) = relative_sims(i,k) * weight(k)
            so that the item with similarity=1 has similarity=weight(k),
            this way the cluster's weight will influence the item's final score.

        - The final score of each item is then calculated by summing the item's partial scores across all cluster:
            score(i) = Σ(partial_score(i,k) for each k.
        """

        def scale01(val, lst):
            return (val - min(lst)) / (max(lst) - min(lst))

        for cluster in clusters:
            relative_sims = {}
            for candidate in self.candidates:
                item = candidate.item
                similarity = self.__cosine_similarity(cluster["centroid"], json.loads(item.vector))
                relative_sims[item.wkd_id] = similarity     
            normalized_sims = {itemid: scale01(similarity, relative_sims.values()) for itemid, similarity in relative_sims.items()}

            for candidate in self.candidates:
                candidate.score += (normalized_sims[candidate.item.wkd_id]) * cluster['weight']

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

        current_toprint = self.current if 'abstract' not in self.current.keys() else list(filter(lambda x: x[0] != 'abstract', self.current.items()))
        print(f'[{self.i}/{self.tot}] {current_toprint}')


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
        # self.input_set = self.input_set[:3] # for testing
        super().initialize()

    def retrieve_next(self):
        # utils.disablePrint()
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
        # utils.enablePrint()


class GeoItemRetriever(ItemRetriever):
    def __init__(self, media_type, limit=None):
        self.limit = limit
        super().__init__(media_type)

    def initialize(self, geoarea):
        self.input_set = []
        print(f'{type(self).__name__} for {self.mtype}: initializing...')
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


class PoiItemRetriever(ItemRetriever):
    def __init__(self, media_type, limit=None):
        self.limit = limit
        super().__init__(media_type)

    def initialize(self, poi_name):
        self.input_set = []
        print(f'{type(self).__name__} for {self.mtype}: initializing...')
        spql = lod_queries.Sparql(constants.DBPEDIA, limit=self.limit)
        try:
            bindings = spql.execute(spql.get_query(self.mtype, 'poi', poi_name))
            self.input_set = list(map(lambda x: {
                'id': re.sub('http://www.wikidata.org/entity/', '', x['wkditem']['value']),
                'name': x['label']['value'],
                'abstract': re.sub('\n', ' ', x['abstract']['value'])
            }, bindings))

        except Exception as e:
            print(f'{type(self).__name__} for {self.mtype}: {e}')
        super().initialize()

    def retrieve_next(self):
        super().retrieve_next()
        try: # use cached item
            item = RetrievedItem.objects.get(wkd_id=self.current['id'])
            print(f'\t\"{self.current["name"]}\" found cached: {item.wkd_id}.')

        except RetrievedItem.DoesNotExist: # create new item
            item = RetrievedItem(
                wkd_id=self.current['id'],
                media_type=self.mtype,
                name=self.current['name'],
                abstract=self.current['abstract'],
            )
            item.save()
        
        if item.abstract:
            item.vector = json.dumps(d2v.create_vector(item.abstract, self.mtype).tolist())
            item.save() # update item adding vector
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

    def recommend(self, method='summarize', strip=False):
        # utils.disablePrint()
        """Before calling this function, be sure that the recommender's retriever has retrieved items."""
        itemids = self.retriever.retrieved_items
        if not itemids:
            raise utils.RetrievalError
        items = [RetrievedItem.objects.get(wkd_id=itemid) for itemid in itemids]
        
        print(f'{type(self).__name__}: recommending using method "{method}"')
        ranker = ItemRanker(items, strip)
        if method == 'clustering':
            clusters = Clusterer().dbscan(self.uservectors, constants.CLUSTERING_EPS)
            ranking = ranker.rank_items_using_clusters(clusters)

        elif method == 'summarize':
            sum_vec = sum(np.array(self.uservectors))
            ranking = ranker.rank_items_using_sum(sum_vec)

        elif method == 'outdegree':
            ranking = ranker.rank_items_outdegree()

        # utils.enablePrint()
        return ranking
