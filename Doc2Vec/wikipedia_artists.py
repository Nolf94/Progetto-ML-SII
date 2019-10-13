import urllib.request
import urllib.parse
import json
import re
import os

os.system("rm -r data_artists.txt")

df = open("artists.txt")
i = 0

for line in df:
    artist = re.sub("(.*)<SEP>(.*)<SEP>(.*)<SEP>", "", line).strip()

    linkid = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(artist)
    link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=0&titles=" \
           + urllib.parse.quote(str(artist).encode('utf-8'))


    try:
        contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote("_(band)")).read()
        pageid = json.loads(contents)
        id = pageid['pageid']


        contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote("_(band)")).read()
        extract = json.loads(contents2)
        try:
            abstract = extract['query']['pages'][str(id)]['extract']

        except KeyError as keyerror:
            continue

        abstract = re.sub('\n', '', abstract)

    except urllib.error.HTTPError as error:
        if error.code == 404:
            try:
                contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote("_(singer)")).read()
                pageid = json.loads(contents)
                id = pageid['pageid']
                contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote("_(singer)")).read()
                extract = json.loads(contents2)
                try:
                    abstract = extract['query']['pages'][str(id)]['extract']
                except KeyError as keyerror:
                    continue

                abstract = re.sub('\n', '', abstract)
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    try:
                        contents = urllib.request.urlopen(linkid).read()
                        pageid = json.loads(contents)
                        id = pageid['pageid']
                        contents2 = urllib.request.urlopen(link.rstrip()).read()
                        extract = json.loads(contents2)


                        if 'query' in extract:
                            query = extract['query']
                            if 'redirects' in query:
                            #[a['name'] for a in aaa['data']['array'] if a['id']=='1']
                                try:
                                    tofrag = [a['tofragment'] for a in query['redirects']]
                                    if tofrag:
                                        continue
                                except KeyError as keyerror:
                                    print("Not Found!")

                        try:
                            abstract = extract['query']['pages'][str(id)]['extract']
                        except KeyError as keyerror:
                            continue

                        abstract = re.sub('\n', '', abstract)

                    except urllib.error.HTTPError as error:
                        if error.code == 404:
                            continue

    with open('data_artists.txt', 'a', encoding='utf-8') as f:
        if ("may refer to:" not in abstract and "may also refer to:" not in abstract):
            print(str(i) + " " + abstract)
            f.write(abstract + '\n')
    i += 1
