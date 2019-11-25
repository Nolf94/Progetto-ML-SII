import json
import re
import urllib.error
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPHandler, urlopen

from SPARQLWrapper import JSON, SPARQLExceptions, SPARQLWrapper

from lodreranker import constants
from lodreranker.models import RetrievedItem


class Sparql(object):
    """Interface for building and executing SPARQL queries to the Wikidata endpoint."""

    def __init__(self, lod, limit=constants.SPARQL_LIMIT_DEFAULT):
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        
        if lod in constants.SUPPORTED_LODS:
            sparql = SPARQLWrapper(lod, agent=agent)
            self.lod = lod
        else:
            raise Exception(f"Invalid lod: {lod}")

        sparql.setTimeout(constants.SPARQL_TIMEOUT)
        sparql.setReturnFormat(JSON)
        self.sparql = sparql
        self.limit = limit


    # QUERYSTRING QUERIES --------------------------------------------------------------------------------
    # SLOW! Given a string, they check the existence of a wikidata item with a label containing that string.
    # If found, the item is returned (1 item per query)
    """DEPRECATED"""
    def get_query_movies_querystring(self, qs):
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
    
    """DEPRECATED"""
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

    """DEPRECATED"""
    def get_query_artists_querystring(self, qs):
        query = """
            SELECT DISTINCT ?label ?item 
            WHERE { 
                    {      
                        ?item wdt:P106 ?type.
                        ?type wdt:P279 wd:Q2643890.
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

    
    # LIGHT QUERIES --------------------------------------------------------------------------------
    # They only check the type of a wikidata item, given its id (fast).
    # If found, the item is returned (1 item per query)

    def get_query_movies_light(self, wkd_id):
        query = """
        SELECT ?type ?typeLabel
        WHERE {
            BIND(wd:"""f'{wkd_id}'""" as ?item)
            ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q11424.         # item has type which (is subclass of)* film
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en, it". }
        }
        """
        return query

    def get_query_books_light(self, wkd_id):
        query = """
        SELECT ?type ?typeLabel
        WHERE {
            BIND(wd:"""f'{wkd_id}'""" as ?item)
            ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q47461344.      # item has type which (is subclass of)* written work
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en, it". }
        }
        """
        return query

    def get_query_artists_light(self, wkd_id):
        query = """
        SELECT ?type ?typeLabel
        WHERE {
            BIND(wd:"""f'{wkd_id}'""" as ?item)
            # two cases because -types- of humans are expressed using occupation (P106)
            {
                # groups of humans: bands, orchestras etc.
                ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q32178211.  # item has type which (is subclass of)* music organisation
            }
            UNION
            {
                # humans: singers, instrument players, performers, composers etc.
                ?item wdt:P106/wdt:P279* ?occupations.          # item has occupation which (is subclass of)* occupations
                VALUES ?occupations { wd:Q639669 wd:Q1294626 }  # occupations is musician OR music artist
            }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en, it". }
        }
        """
        return query


    # GEOLOCALIZED QUERIES --------------------------------------------------------------------------------
    # Given a set of coordinates and a radius, they check the existence of wikidata items within that area
    # If found, the item is returned (1 item per query)

    def get_query_movies_geolocalized(self, geoarea):
        query = """
        SELECT DISTINCT ?item ?itemLabel ?linkCount (count(distinct ?entity) as ?outDegree) 
        WHERE {
            ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q11424; # item has type which (is subclass of)* film
                ?placePred ?place;                      # item has a placePred relation with place
                rdfs:label ?itemLabel;
                wikibase:sitelinks ?linkCount;
                ?p ?entity.
            VALUES ?placePred { wdt:P840 wdt:P915 }     # placePred is narrative location OR filming location
            SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            SERVICE wikibase:around {
                ?place wdt:P625 ?location.
                bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                                wikibase:radius """f'"{geoarea.rad}"'""".
            }
            FILTER((LANG(?itemLabel)) = "it")
            FILTER(STRSTARTS(STR(?entity), "http://www.wikidata.org/entity/"))
        }
        GROUP BY ?item ?itemLabel ?linkCount ?outDegree
        # ORDER BY DESC (?linkCount) # for external wikibase links (wikipedia, wikiquote etc.)
        ORDER BY DESC (?outDegree) # for internal (wikidata) links between entities
        LIMIT """f'{self.limit}'"""
        """
        return query

    def get_query_books_geolocalized(self, geoarea):
        query = """
        SELECT DISTINCT ?item ?itemLabel ?linkCount (count(distinct ?entity) as ?outDegree) 
        WHERE {
            ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q47461344.  # item has type which (is subclass of)* written work
                rdfs:label ?itemLabel;
                wikibase:sitelinks ?linkCount;
                ?p ?entity.
            {
                ?item wdt:P840 ?place.   # item narrative location is place 
            }
            UNION
            {
                ?author wdt:P50 ?item;   # author is author of item
                    wdt:P106 wd:Q36180.  # author occupation is a writer
                    wdt:P19 ?place;      # author was born in place
            }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            SERVICE wikibase:around {
                ?place wdt:P625 ?location.
                bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                                wikibase:radius """f'"{geoarea.rad}"'""".
            }
            FILTER((LANG(?itemLabel)) = "it")
            FILTER(STRSTARTS(STR(?entity), "http://www.wikidata.org/entity/"))
        }
        GROUP BY ?item ?itemLabel ?linkCount ?outDegree
        # ORDER BY DESC (?linkCount) # for external wikibase links (wikipedia, wikiquote etc.)
        ORDER BY DESC (?outDegree) # for internal (wikidata) links between entities
        LIMIT """f'{self.limit}'"""
        """
        return query

    def get_query_artists_geolocalized(self, geoarea):
        query = """
        SELECT DISTINCT ?item ?itemLabel ?linkCount (count(distinct ?entity) as ?outDegree) 
        WHERE {
            # two cases because -types- of humans are expressed using occupation (P106)
            {
                # groups of humans: bands, orchestras etc.
                ?item (p:P31/ps:P31/(wdt:P279*)) wd:Q32178211;  # item has type which (is subclass of)* music organisation
                    wdt:P740 ?place.                            # item location of formation is place
            }
            UNION
            {
                # humans: singers, instrument players, performers, composers etc.
                ?item wdt:P106/wdt:P279* ?occupations;          # item has occupation which (is subclass of)* occupations
                    wdt:P19 ?place.                             # item was born in place
                VALUES ?occupations { wd:Q639669 wd:Q1294626 }  # occupations is musician OR music artist
            }
            ?item rdfs:label ?itemLabel;
                wikibase:sitelinks ?linkCount;
                ?p ?entity.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
            SERVICE wikibase:around {
                ?place wdt:P625 ?location.
                bd:serviceParam wikibase:center """f'"Point({geoarea.lng} {geoarea.lat})"'"""^^geo:wktLiteral;
                                wikibase:radius """f'"{geoarea.rad}"'""".
            }
            FILTER((LANG(?itemLabel)) = "it")
            FILTER(STRSTARTS(STR(?entity), "http://www.wikidata.org/entity/"))
        }    
        GROUP BY ?item ?itemLabel ?linkCount ?outDegree
        # ORDER BY DESC (?linkCount) # for external wikibase links (wikipedia, wikiquote etc.)
        ORDER BY DESC (?outDegree) # for internal (wikidata) links between entities
        LIMIT """f'{self.limit}'"""
        """
        return query


    # DBPEDIA POI QUERIES --------------------------------------------------------------------------------

    def get_query_movies_poi(self, qs):
        query = """
        SELECT DISTINCT ?label ?abstract 
        FROM <http://dbpedia.org/page_links>
        WHERE {
            ?poi rdfs:label """f'"{qs}"'"""@it.
            ?item dbo:wikiPageWikiLink ?poi;
                rdf:type schema:Movie;
                rdfs:label ?label;
                dbo:abstract ?abstract.
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
            ?item dbo:wikiPageWikiLink ?poi.
            {
                ?item rdf:type  schema:Book;
                    rdfs:label ?label;
                    dbo:abstract ?abstract.             
            }
            UNION 
            {
                ?item rdf:type  dbo:Writer.
                ?book dbo:author ?item;
                    rdfs:label ?label;
                    dbo:abstract ?abstract.            
            }
            FILTER langMatches(lang(?abstract),"en")    
            FILTER langMatches(lang(?label),"en")    
        }
        GROUP BY ?label
        """
        return query
            
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
        return query

    #  ---------------------------------------------------------------------------------------------------

    def execute(self, query):
        self.sparql.setQuery(query)
        try:
            result = self.sparql.query()
            bindings = result.convert()['results']['bindings']
            if not bindings:
                raise Exception("No match found.")
            return bindings
        except HTTPError as e:
            raise Exception(f'HTTPError {e.code}, {str(e)}')
        except Exception as e:
            raise Exception(str(e))

    def get_query(self, media_type, query_type, query_args):
        wkd_types = ['light', 'querystring', 'geolocalized']
        dbp_types = ['poi']

        if ((self.lod == constants.WIKIDATA and not query_type in wkd_types) or
                (self.lod == constants.DBPEDIA and not query_type in dbp_types)):
            raise Exception(f"Invalid query_type '{query_type}' for endpoint '{self.lod}'")

        return getattr(self, f'get_query_{media_type}_{query_type}')(query_args)


class Wikibase(object):
    """Interface for executing queries to the Wikibase APIs."""

    def search(self, querystring, limit=7):
        """
        Searches the Wikidata API with the given querystring.
        Returns a list of entities with their wikidata item id.
        """
        wkd_query_params = urlencode({
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'it',
            'limit': limit,
            'search': querystring,
        })
        wkd_query = f'https://www.wikidata.org/w/api.php?{wkd_query_params}'
        wkd_results = json.loads(urlopen(wkd_query.rstrip()).read().decode('utf-8'))
        return wkd_results['search']

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
