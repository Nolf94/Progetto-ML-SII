import urllib.request
import urllib.parse
import json
import re
import os

os.system("rm -r data_books.txt")

df = open("booksummaries.txt")
i = 0

for line in df:
    wikiID = line.split("/")[0].rstrip()
    try:
        url = urllib.request.urlopen("https://en.wikipedia.org/w/api.php?format=json&action=query&prop=info&pageids="+ wikiID +"&inprop=url").read()
        pageid = json.loads(url)
        canonicalURL = pageid['query']['pages'][str(wikiID)]['canonicalurl']

        title = re.sub('https://en.wikipedia.org/wiki/', '', canonicalURL)

        link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" \
            + urllib.parse.quote(title)

        try:
            contents = urllib.request.urlopen(link).read()
            extract = json.loads(contents)

            try:
                abstract = extract['query']['pages'][str(wikiID)]['extract']
            except KeyError as keyerror:
                continue

            abstract = re.sub('\n', '', abstract)

        except urllib.error.HTTPError as error:
            if error.code == 404:
                continue

    except KeyError as keyerror:
        continue

    with open('data_books.txt', 'a', encoding='utf-8') as f:
        print(str(i) + " " + abstract)
        f.write(abstract + '\n')

    i += 1