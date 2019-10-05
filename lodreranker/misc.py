import json
import urllib.request

import requests
from SPARQLWrapper import JSON, SPARQLWrapper


class Lod_queries:
    def retrieveFilmAbstract(self, film):
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setQuery("""
               prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
               prefix dbpedia-owl: <http://dbpedia.org/ontology/>
               SELECT DISTINCT ?film ?abstract  WHERE  {
                   ?film a dbpedia-owl:Filmw.
                   ?film rdfs:label ?label .
                   FILTER regex( str(?label),"""f'"{film}"'""", "i")
                   ?film dbpedia-owl:abstract ?abstract .
                   FILTER langMatches(lang(?abstract),"en")
                   }
                   LIMIT 10
                        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        data =[]
        for result in results["results"]["bindings"]:
            data.append(result["abstract"]["value"])
        return data
