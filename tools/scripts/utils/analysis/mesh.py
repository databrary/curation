import requests
from urllib import urlencode
import sys, os
import csv, json

#input_file = sys.argv[1]

_TEST_TERMS = ["infant", "perception", "cognition"]

def getMesh(term):
    _base = "http://id.nlm.nih.gov/mesh/sparql"
    _q = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#> PREFIX mesh: <http://id.nlm.nih.gov/mesh/> PREFIX mesh2015: <http://id.nlm.nih.gov/mesh/2015/> SELECT ?d ?dName ?c ?n FROM <http://id.nlm.nih.gov/mesh> WHERE { ?c meshv:scopeNote ?n . ?d meshv:concept ?c . ?d rdfs:label ?dName . FILTER(REGEX(?dName,'%s','i'))}" % (term)
    _inference = "true"
    _format = "JSON"     
    params = {"query":_q,
              "format": _format,
              "inference": _inference}
    res = requests.get(url=_base, params=params)
    return res

def getCSV(csv):
    pass

def parseResults(res):
    pass

def main(terms):
    for t in terms:
        results = getMesh(t)
        data = json.loads(results.text)
        print(data)
        
if __name__ == '__main__':
    main(_TEST_TERMS)



