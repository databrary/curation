from SPARQLWrapper import SPARQLWrapper, JSON
import sys, os
import csv, json, simplejson

#input_file = sys.argv[1]


def main():
    

def getMesh(term):
    qString = """ 
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                  PREFIX owl: <http://www.w3.org/2002/07/owl#>
                  PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
                  PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                  PREFIX mesh2015: <http://id.nlm.nih.gov/mesh/2015/>

                  SELECT ?d ?dName ?c ?n
                  FROM <http://id.nlm.nih.gov/mesh>
                  WHERE {
                    ?c meshv:scopeNote ?n .
                    ?d meshv:concept ?c .
                    ?d rdfs:label ?dName .
                    FILTER(REGEX(?dName,'%s','i'))
                   } """ % (term)
                  
    sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
    sparql.setQuery(qString)
    sparql.setReturnFormat(JSON)
    res = sparql.query().convert()
    return res

def getCSV(csv):
    pass

def parseResults(res):
    pass


if __name__ == '__main__':
    main()



