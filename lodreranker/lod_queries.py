import json
import re
import urllib.error
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPHandler, urlopen

from SPARQLWrapper import JSON, SPARQLExceptions, SPARQLWrapper

import Doc2Vec.doc2vec as d2v
from lodreranker import constants

from .models import RetrievedItem

SPARQL_TIMEOUT = 60  # set the query timeout (in seconds)
SPARQL_LIMIT = 30 # TODO increase dynamically

class Sparql(object):
    """Interface for building and executing SPARQL queries to the Wikidata endpoint."""

    def __init__(self):
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36")
        sparql.setTimeout(SPARQL_TIMEOUT)
        sparql.setReturnFormat(JSON)
        self.sparql = sparql

    def get_query_movies_querystring(self, qs):
            # filmtype_ids = ['Q11424', 'Q93204', 'Q226730', 'Q185529', 'Q200092', 'Q188473', 'Q24862', 'Q157443', 'Q319221', 'Q202866', 'Q219557', 'Q229390', 'Q506240', 'Q31235', 'Q645928', 'Q517386', 'Q842256', 'Q459290', 'Q1054574', 'Q369747', 'Q848512', 'Q24869', 'Q130232', 'Q959790', 'Q1067324', 'Q505119', 'Q652256', 'Q790192', 'Q1268687', 'Q1060398', 'Q12912091', 'Q2143665', 'Q663106', 'Q677466', 'Q336144', 'Q1935609', 'Q1146335', 'Q1200678', 'Q2165644', 'Q1361932', 'Q2484376', 'Q2973181', 'Q3250548', 'Q596138', 'Q2321734', 'Q2301591', 'Q1320115', 'Q430525', 'Q7130449', 'Q1251417', 'Q20442589', 'Q24865', 'Q3072043', 'Q3585697', 'Q917641', 'Q2125170', 'Q2903140', 'Q3677141', 'Q455315', 'Q3648909', 'Q370630', 'Q7858343', 'Q16909344']
            # filmtypes = ' '.join(f'wd:{x}' for x in filmtype_ids)
            # ?item wdt:P31 ?type.
            # VALUES ?type { """f'{filmtypes}'""" }
        query = """
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
                ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q11424.
                ?item rdfs:label ?queryByTitle.
                ?item wikibase:sitelinks ?sitelinks
                FILTER(lang(?queryByTitle) = 'it' || lang(?queryByTitle) = 'en')
                FILTER(REGEX(?queryByTitle, """f'"{qs}"'""", "i"))
                SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            }    
            ORDER BY DESC(?sitelinks) 
            LIMIT 1
            """
        return query

        # bd:serviceParam wikibase:language "it,en,fr,ar,be,bg,bn,ca,cs,da,de,el,es,et,fa,fi,he,hi,hu,hy,id,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh". 
    def get_query_books_querystring(self, qs):
        query = """
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
                ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q17537576.
                ?item rdfs:label ?queryByTitle.
                ?item wikibase:sitelinks ?sitelinks
                FILTER(lang(?queryByTitle) = 'it' || lang(?queryByTitle) = 'en')
                FILTER(REGEX(?queryByTitle, """f'"{qs}"'""", "i"))
                SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            }    
            ORDER BY DESC(?sitelinks) 
            LIMIT 1
            """
        return query

    def get_query_artists_querystring(self, qs):
        query = """
            SELECT DISTINCT ?label ?item ?sitelinks
            WHERE { 
                    {      
                        ?type wdt:P279 wd:Q2643890.
                        ?item wdt:P106 ?type.
                    }       
                    UNION
                    {
                        ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q215380.
                    }
                    ?item rdfs:label ?label.
                    ?item wikibase:sitelinks ?sitelinks
                    FILTER(lang(?label) = 'it' || lang(?label) = 'en')
                    FILTER(REGEX(?label, """f'"{qs}"'""", "i"))
            }
            ORDER BY DESC (?sitelinks)
            LIMIT 1
            """
        return query

    def get_query_movies_geolocalized(self, geoarea):
        query = """
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {
                ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q11424;
                    wdt:P840 ?place;
                    rdfs:label ?itemLabel;
                    wikibase:sitelinks ?linkCount.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
                SERVICE wikibase:around {
                    ?place wdt:P625 ?location.
                    bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                                    wikibase:radius """f'"{geoarea.rad}"'""".
                }
                FILTER((LANG(?itemLabel)) = "it")
            }
            GROUP BY ?item ?itemLabel
            ORDER BY DESC (?linkCount)
            LIMIT """f'{SPARQL_LIMIT}'"""
            """
        return query

    def get_query_books_geolocalized(self, geoarea):
        query = """
        SELECT DISTINCT ?item ?itemLabel 
        WHERE { 
                {
                    VALUES ?type {wd:Q47461344 wd:Q7725634}
                    ?item (p:P31/ps:P31/(wdt:P279*)) ?type;
                }
                UNION
                {   ?author wdt:P569 ?place.
                    ?author wdt:P106 wd:Q36180.
                    ?author wdt:P50 ?item
                }
                ?item wdt:P840 ?place.
                ?item rdfs:label ?itemLabel.
                ?item wikibase:sitelinks ?linkCount.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
                SERVICE wikibase:around {
                ?place wdt:P625 ?location.
                bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                                wikibase:radius """f'"{geoarea.rad}"'""".
                }
                FILTER((LANG(?itemLabel)) = "it")
        }
        GROUP BY ?item ?itemLabel
        ORDER BY DESC (?linkCount)
        """

    def get_query_artists_geolocalized(self, geoarea):
        query = """
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {
                {
                 ?type wdt:P279* wd:Q639669.
                 ?item wdt:P106 ?type.
                 ?item wdt:P19 ?place.
                 }
            UNION
                 {
                  ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q215380.
                  ?item wdt:P740 ?place
                 }
            ?item rdfs:label ?itemLabel.
            ?item wikibase:sitelinks ?linkCount.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            SERVICE wikibase:around {
            ?place wdt:P625 ?location.
            bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                             wikibase:"""f'"{geoarea.rad}"'""".}
            FILTER((LANG(?itemLabel)) = "it")
                 }
             
            GROUP BY ?item ?itemLabel
            ORDER BY DESC (?linkCount)
            LIMIT """f'{SPARQL_LIMIT}'"""
             """

    def get_query_movies_poi(self, qs):
        query = """
            SELECT DISTINCT ?label ?abstract 
            FROM <http://dbpedia.org/page_links>
            WHERE {
                ?o  dbo:wikiPageWikiLink ?poi.
                ?poi rdfs:label """f'"{qs}"'"""@it.
                ?o  rdf:type schema:Movie.
                ?o  rdfs:label ?label.
                ?o  dbo:abstract ?abstract
                FILTER langMatches(lang(?abstract),"en")    
                FILTER langMatches(lang(?label),"en")                   
                 }
            GROUP BY ?label
            """
        return query

    def get_query_books_poi(self, qs):
        query = """
            SELECT DISTINCT ?label ?abstract 
            FROM <http://dbpedia.org/page_links>
            WHERE { 
                   ?poi rdfs:label """f'"{qs}"'"""@it.
                   ?o dbo:wikiPageWikiLink ?poi.
                   {
                      ?o  rdf:type  schema:Book.
                      ?o  rdfs:label ?label.
                      ?o  dbo:abstract ?abstract               
                   }
            UNION 
                   {
                     ?o  rdf:type  dbo:Writer.
                     ?book  dbo:author ?o  .
                     ?book rdfs:label ?label.
                     ?book  dbo:abstract ?abstract               
                    }
            FILTER langMatches(lang(?abstract),"en")    
            FILTER langMatches(lang(?label),"en")    
            }
            GROUP BY ?label
            """
            
    def get_query_artists_poi(self, qs):
        query = """
            SELECT DISTINCT ?label ?abstract 
            FROM <http://dbpedia.org/page_links>
            WHERE { 
                    ?o  dbo:wikiPageWikiLink ?poi.
                    ?poi rdfs:label """f'"{qs}"'"""@it.
                    {
                     ?o  rdf:type  dbo:MusicalWork.
                     ?o  dbo:artist  ?artist.
                     ?artist  rdfs:label ?label.
                     ?artist  dbo:abstract ?abstract                  
                    }
                    UNION
                    {
                     ?o  rdf:type  schema:MusicGroup.
                     ?o  rdfs:label ?label.
                     ?o  dbo:abstract ?abstract          
                    }
                    FILTER langMatches(lang(?abstract),"en")    
                    FILTER langMatches(lang(?label),"en") 
            }
            GROUP BY ?label
            """

    def execute(self, query):
        self.sparql.setQuery(query)
        try:
            result = self.sparql.query()
            bindings = result.convert()['results']['bindings']
            if not bindings:
                raise Exception("Nothing found.")
            return bindings
        except HTTPError as e:
            raise Exception(f'HTTPError {e.code}, {str(e)}')
        except Exception as e:
            raise Exception(str(e))


class Wiki(object):
    """Interface for executing queries to the Wiki legacy APIs."""

    def retrieve_abstract(self, item):
        """
        Given an item with a Wikidata item ID, executes the following queries:
        - Query the Wikidata API to get the Wiki page title from the wikidata item ID.
        - Query the Wikipedia extracts API with the page title to get the page's first paragraph (our abstract).
        """
        try:
            try:
                # Query wikidata API to get wikipedia pagetitle from wkd_id
                wkd_query_params = urlencode({
                'action': 'wbgetentities',
                'format': 'json',
                'props': 'sitelinks',
                'ids': item.wkd_id,
                'sitefiter': 'enwiki'
                })
                wkd_query = f'https://www.wikidata.org/w/api.php?{wkd_query_params}'
                wkd_item = json.loads(urlopen(wkd_query.rstrip()).read().decode('utf-8'))
                wiki_page_title = wkd_item['entities'][item.wkd_id]['sitelinks']['enwiki']['title']
                print(f'\t"{item.wkd_id}": found page "{wiki_page_title}".')

                # Query wikipedia API to get abstract from wikipedia pagetitle
                    # We use the old wikipedia API because the following query:
                    #   https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page_title}
                    # returns just the first paragraph of the summary. We need the whole block instead.
                    # Parameters:
                    #   exintro      -> return only the content before the first section (our abstract)
                    #   explaintext  -> extract plain text instead of HTML
                    #   indexpageids -> include additional page ids section listing all returned page IDS 
                    #                   (useful since we don't want to know the page ID).
                wiki_extracts_query_params = urlencode({
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts',
                    'redirects': 1,
                    'titles': wiki_page_title
                })
                wiki_extracts_query_params_additional = '&'.join(['exintro', 'explaintext', 'indexpageids'])
                wiki_extracts_query = f'https://en.wikipedia.org/w/api.php?{wiki_extracts_query_params}&{wiki_extracts_query_params_additional}'
                response = json.loads(urlopen(wiki_extracts_query.rstrip()).read())['query']
                wiki_page_id = response['pageids'][0]
                abstract = response['pages'][str(wiki_page_id)]['extract']
                abstract = re.sub('\n', ' ', abstract)
                print(f'\t"{wiki_page_title}": retrieved {len(abstract)} characters.')
                return abstract

            except HTTPError as e:
                raise Exception(f'HTTPError {e.code}, {str(e)}.')
            except KeyError as e:
                raise Exception(f'KeyError, missing {str(e)}.')
            except Exception as e:
                raise Exception(str(e))
        except Exception as e:
            print(f'\t{e}')
            return None