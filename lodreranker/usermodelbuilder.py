import json
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

import requests
from SPARQLWrapper import JSON, SPARQLWrapper

from Doc2Vec.doc2vec_films_vectors import create_vector
from Doc2Vec.doc2vec_preprocessing import normalize_text, stopping
from Clustering.Clustering import clusterize

from .sparql_utils import get_movie_query

class UserModelBuilder(object):
    MOVIES = 'movies'
    BOOKS = 'books'
    MUSIC = 'music'

    MEDIA_TYPES = [MOVIES, BOOKS, MUSIC]

    def retrieveWikidataItem(self, element, media_type):
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36")
        
        if media_type == self.MOVIES:  
            query = get_movie_query(element)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        bindings = sparql.query().convert()['results']['bindings']
        if bindings:
            return bindings[0]['item']['value']
        else:
            raise Exception(f'\t"{element}": item not found')


    def get_wikipedia_abstract(self, querystring, media_type):
        try:
            print(f'- "{querystring}"')
            wiki_url = self.retrieveWikidataItem(querystring, media_type)
            if wiki_url:
                wkd_id = re.sub('http://www.wikidata.org/entity/','', wiki_url)
                print(f'\t"{querystring}" returned item: {wkd_id}.')
                wkd_query = f'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids={wkd_id}&sitefilter=enwiki'
                wkd_item = json.loads(urlopen(wkd_query.rstrip()).read().decode('utf-8'))
                wiki_page_title = wkd_item['entities'][wkd_id]['sitelinks']['enwiki']['title']
                print(f'\t"{querystring}": found page "{wiki_page_title}".')
            
                # We use the old wikipedia API because the following query:
                #   https://en.wikipedia.org/api/rest_v1/page/summary/{quote(wiki_title)}
                # returns just the first paragraph of the summary. We need the whole block instead.
                # Parameters:
                #   exintro -> return only the content before the first section (our abstract)
                #   explaintext -> extract plain text instead of HTML
                #   indexpageids -> include additional page ids section listing all returned page IDS (useful since we don't want to know the page ID).

                wiki_extracts_query = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&indexpageids&redirects=1&titles=' \
                    + quote(wiki_page_title)
                print(f'\t"{wiki_page_title}": fetching abstract...')
                response = json.loads(urlopen(wiki_extracts_query.rstrip()).read())['query']
                wiki_page_id = response['pageids'][0]
                abstract = response['pages'][str(wiki_page_id)]['extract']
                
                return re.sub('\n', '', abstract)

        except HTTPError as error:
            if error.code == 404:
                return
        except KeyError as e:
            print(f'\t"{querystring}": keyerror, missing {str(e)}')
            return
        except Exception as e:
            print(str(e))
            return


    def get_vectors_from_social(self, extra_data_media, media_type):
        if media_type not in self.MEDIA_TYPES:
            print('Error: bad media type')
            return

        media = extra_data_media['data']
        has_next = 'next' in extra_data_media['paging'].keys()
        while has_next:
            next_page = json.loads(urlopen(extra_data_media['paging']['next']).read().decode('utf-8'))
            media.extend(next_page['data'])
            has_next = 'next' in next_page['paging'].keys()

        abstracts = []
        media = media[:5] #for testing purposes only

        print(f'Retrieving abstracts for {len(media)} {media_type}:')
        for element in media:
            # TODO improve query performance (or make it non-blocking)
            abstract = self.get_wikipedia_abstract(element['name'], media_type)
            if abstract:
                abstracts.append(normalize_text(stopping(abstract)))
        print(f'Retrieved {len(abstracts)} abstracts (number of non-{media_type} elements: {len(media)-len(abstracts)}).')

        vectors = []
        for abstract in abstracts:
            vectors.append(create_vector(abstract))
        return vectors


    def build_model(self, vector_list):
        return clusterize(vector_list)
