import json
import urllib.request

import requests
from SPARQLWrapper import JSON, SPARQLWrapper


class Lod_queries:
    def retrieveFilmAbstract(self, film):
        sparql = SPARQLWrapper("https://query.wikidata.org")
        sparql.setQuery
        ("""
                SELECT DISTINCT ?item ?name WHERE {
                VALUES ?type {wd:Q11424} ?item wdt:P31 ?type .
                ?item rdfs:label ?queryByTitle.
                ?item wdt:P1476 ?name.
                FILTER(REGEX(?queryByTitle, """f'"{film}"'""", "i"))
                }
                LIMIT 100
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        data =[]
        for result in results["results"]["bindings"]:
            data.append(result["item"]["value"])
        return data
