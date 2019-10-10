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
    link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" \
           + urllib.parse.quote(str(artist).encode('utf-8'))

    try:
        contents = urllib.request.urlopen(linkid).read()
        pageid = json.loads(contents)
        id = pageid['pageid']
        contents2 = urllib.request.urlopen(link).read()
        extract = json.loads(contents2)
        try:
            abstract = extract['query']['pages'][str(id)]['extract']
        except KeyError as keyerror:
            continue

        abstract = re.sub('\n', '', abstract)

        with open('data_artists.txt', 'a', encoding='utf-8') as f:
            if ("may refer to:" not in abstract and "may also refer to:" not in abstract):
                print(str(i) + " " + abstract)
                f.write(abstract + '\n')

    except urllib.error.HTTPError as error:
        if error.code == 404:
            continue
    i +=1

'''
for column in saved_column:

    column = re.sub(r" ?\([^)]+\)", '', column)

    linkid = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(column)
    link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" \
            + urllib.parse.quote(str(column).encode('utf-8'))
    try:
        contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote("_(novel)")).read()
        pageid = json.loads(contents)
        id = pageid['pageid']
        contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote("_(novel)")).read()
        extract = json.loads(contents2)
        try:
            abstract = extract['query']['pages'][str(id)]['extract']
        except KeyError as keyerror:
            continue

        abstract = re.sub('\n', '', abstract)

        with open('data_books.txt', 'a', encoding='utf-8') as f:
            if ("may refer to:" not in abstract and "may also refer to:" not in abstract):
                print(str(i) + " " + abstract)
                f.write(abstract + '\n')

    except urllib.error.HTTPError as error:
        if error.code == 404:
            try:
                contents = urllib.request.urlopen(linkid).read()
                pageid = json.loads(contents)
                id = pageid['pageid']
                contents2 = urllib.request.urlopen(link.rstrip()).read()
                extract = json.loads(contents2)
                try:
                    abstract = extract['query']['pages'][str(id)]['extract']
                except KeyError as keyerror:
                    continue
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    continue


    i += 1





    linkid = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(column)
    link = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles="+ urllib.parse.quote(column)
    try:
        contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote("_(novel)")).read()
        pageid = json.loads(contents)
        id = pageid['pageid']
        contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote("_(novel)")).read()
        extract = json.loads(contents2)
        try:
            abstract = extract['query']['pages'][str(id)]['extract']
        except KeyError as keyerror:
            continue

        abstract = re.sub('\n', '', abstract)

        with open('data_books.txt', 'a', encoding='utf-8') as f:
            if("may refer to:" not in abstract and "may also refer to:" not in abstract):
                print(str(i) + " " + abstract)
                f.write(abstract+'\n')

    except urllib.error.HTTPError as error:
        if error.code == 404:
            continue
    i += 1


       if data['type']=="disambiguation":
            try:
                stringa = "_(novel)"
                contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote(stringa)).read()
                pageid = json.loads(contents)
                id = pageid['pageid']
                contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote(stringa)).read()
                extract = json.loads(contents2)
                try:
                    abstract = extract['query']['pages'][str(id)]['extract']

                except KeyError as keyerror:
                    continue

            except urllib.error.HTTPError as err:
                if err.code == 404:
                    contents = urllib.request.urlopen(linkid.rstrip() + urllib.parse.quote("_(novel)")).read()
                    pageid = json.loads(contents)
                    id = pageid['pageid']
                    contents2 = urllib.request.urlopen(link.rstrip() + urllib.parse.quote("_(novel)")).read()
                    extract = json.loads(contents2)
                    try:
                        abstract = extract['query']['pages'][str(id)]['extract']
                    except KeyError as keyerror:
                        continue
'''