import json
import urllib.request

import requests
from SPARQLWrapper import JSON, SPARQLWrapper


# TODO improve query to avoid false positives
def retrieveFilmAbstract(film):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36")
    query = """
        SELECT DISTINCT ?item WHERE {
        VALUES ?type """"{""wd:Q11424""}"""" ?item wdt:P31 ?type .
        ?item rdfs:label ?queryByTitle.
        ?item wdt:P1476 ?name.
        FILTER(REGEX(?queryByTitle, """f'"{film}"'""", "i"))
        }
        LIMIT 1
        """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    bindings = sparql.query().convert()['results']['bindings']
    if bindings:
        return bindings[0]['item']['value']
    else:
        raise Exception(f'\tElement "{film}" not found')