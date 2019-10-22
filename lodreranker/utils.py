import json
import random
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np
from django.contrib.staticfiles import finders


def get_choices(path='poi'):
    data = open(finders.find(f"js/{path}.json")).read()
    json_data = json.loads(data)
    opts = []

    # json_data = json_data[:3]
    for item in random.sample(json_data, len(json_data)):
    # for item in json_data:
        opts.append(item)
    return opts


def get_poi_weights(selection, choices):
    vectors = []

    for x in selection:
        vectors.append(np.array(choices[int(x)-1]['weights']))
        # print(poi_choices[x-1]['name'])
    # print(vectors)
    # print(sum(vectors))

    weights = sum(vectors)
    return json.dumps(weights.tolist())



def get_wikipedia_abstract(querystring):
    opensearch_query = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={quote(querystring)}&limit=1&namespace=0&format=json"
    result = json.loads(urlopen(opensearch_query.rstrip()).read().decode('utf-8'))
    page_urls = result[3]

    ########### TODO
    # - Use wikidata instead of direct wikipedia
    # - Personalized query for each media type

    if len(page_urls) == 1:
        page_name = re.search('[^\/]+$', page_urls[0]).group(0)
        pageid_query = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_name}"        
        pagecontent_query = f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={page_name}"

        try:
            pageid = json.loads(urlopen(pageid_query.rstrip()).read())['pageid']
            pagecontent = json.loads(urlopen(pagecontent_query.rstrip()).read())
            try:
                abstract = pagecontent['query']['pages'][str(pageid)]['extract']
            except KeyError as keyerror:
                return
        except HTTPError as error:
            if error.code == 404:
                return
        return re.sub('\n', '', abstract)
    else:
        print(f"no article found for querystring {querystring}")
        return
