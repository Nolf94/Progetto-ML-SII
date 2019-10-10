import urllib.request
import urllib.parse
import json
import pandas as pd
import re

df = pd.read_csv("movies_original_dataset.csv")
saved_column = df.Wiki_Page
i = 0

for column in saved_column:
    name = re.sub('https://en.wikipedia.org/wiki/', '', column)
    linkid = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(name)
    link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" + urllib.parse.quote(name)

    try:
        contents = urllib.request.urlopen(linkid.rstrip()).read()
        pageid = json.loads(contents)
        id = pageid['pageid']
        contents2 = urllib.request.urlopen(link.rstrip()).read()
        extract = json.loads(contents2)
        try:
            abstract = extract['query']['pages'][str(id)]['extract']

        except KeyError as keyerror:
            continue

        abstract = re.sub('\n', '', abstract)

        with open('data_film.txt', 'a', encoding='utf-8') as f:
                print(str(i) + abstract)
                f.write(abstract + '\n')

    except urllib.error.HTTPError as error:
        if error.code == 404:
            continue

    i += 1
