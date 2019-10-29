import json
import re
import urllib.error
from urllib.parse import urlencode
from urllib.request import urlopen

from SPARQLWrapper import JSON, SPARQLWrapper

filmtype_ids = ['Q11424', 'Q93204', 'Q226730', 'Q185529', 'Q200092', 'Q188473', 'Q24862', 'Q157443', 'Q319221', 'Q202866', 'Q219557', 'Q229390', 'Q506240', 'Q31235', 'Q645928', 'Q517386', 'Q842256', 'Q459290', 'Q1054574', 'Q369747', 'Q848512', 'Q24869', 'Q130232', 'Q959790', 'Q1067324', 'Q505119', 'Q652256', 'Q790192', 'Q1268687', 'Q1060398', 'Q12912091', 'Q2143665', 'Q663106', 'Q677466', 'Q336144', 'Q1935609', 'Q1146335', 'Q1200678', 'Q2165644', 'Q1361932', 'Q2484376', 'Q2973181', 'Q3250548', 'Q596138', 'Q2321734', 'Q2301591', 'Q1320115', 'Q430525', 'Q7130449', 'Q1251417', 'Q20442589', 'Q24865', 'Q3072043', 'Q3585697', 'Q917641', 'Q2125170', 'Q2903140', 'Q3677141', 'Q455315', 'Q3648909', 'Q370630', 'Q7858343', 'Q16909344']

MOVIES = 'movies'
BOOKS = 'books'
MUSIC = 'music'
MEDIA_TYPES = [MOVIES, BOOKS, MUSIC]


def query_movies(element):
    filmtypes = ' '.join(f'wd:{x}' for x in filmtype_ids)
    query = """
        SELECT DISTINCT ?item
        WHERE   {
            ?item wdt:P31 ?type.
            ?item rdfs:label ?queryByTitle.
            ?item wikibase:sitelinks ?sitelinks
            VALUES ?type { """f'{filmtypes}'""" }
            FILTER(lang(?queryByTitle) = 'it')
            FILTER(REGEX(?queryByTitle, """f'"{element}"'""", "i"))
        }    
        ORDER BY DESC(?sitelinks) 
        LIMIT 1
        """
    return query


def get_wikidata_item_from_string(element, media_type):
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36")
        
        if media_type == MOVIES:  
            query = query_movies(element)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        bindings = sparql.query().convert()['results']['bindings']
        if bindings:
            return bindings[0]['item']['value']
        else:
            raise Exception(f'\t"{element}": item not found')


def get_wikipedia_pagetitle_from_wikidata_itemid(wkd_id):
    wkd_query_params = urlencode({
        'action': 'wbgetentities',
        'format': 'json',
        'props': 'sitelinks',
        'ids': wkd_id,
        'sitefiter': 'enwiki'
    })
    wkd_query = f'https://www.wikidata.org/w/api.php?{wkd_query_params}'
    wkd_item = json.loads(urlopen(wkd_query.rstrip()).read().decode('utf-8'))
    return wkd_item['entities'][wkd_id]['sitelinks']['enwiki']['title']


def get_abstract_from_wikipedia_pagetitle(wiki_page_title):
    # We use the old wikipedia API because the following query:
    #   https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page_title}
    # returns just the first paragraph of the summary. We need the whole block instead.
    # Parameters:
    #   exintro -> return only the content before the first section (our abstract)
    #   explaintext -> extract plain text instead of HTML
    #   indexpageids -> include additional page ids section listing all returned page IDS (useful since we don't want to know the page ID).
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
    return abstract


def get_wikipedia_abstract(querystring, media_type):
    try:
        print(f'- "{querystring}"')
        wkd_url = get_wikidata_item_from_string(querystring, media_type)
        if wkd_url:
            wkd_id = re.sub('http://www.wikidata.org/entity/','', wkd_url)
            print(f'\t"{querystring}" returned item: {wkd_id}.')
            wiki_page_title = get_wikipedia_pagetitle_from_wikidata_itemid(wkd_id)
            print(f'\t"{querystring}": found page "{wiki_page_title}".')
            print(f'\t"{wiki_page_title}": fetching abstract...')            
            abstract = get_abstract_from_wikipedia_pagetitle(wiki_page_title)
            print(f'\t"{wiki_page_title}": retrieved {len(abstract)} characters.')            
            return re.sub('\n', '', abstract)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return
    except KeyError as e:
        print(f'\t"{querystring}": KeyError, missing {str(e)}')
        return
    except Exception as e:
        print(str(e))
        return