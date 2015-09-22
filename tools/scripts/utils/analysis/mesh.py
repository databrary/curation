from SPARQLWrapper import SPARQLWrapper, JSON
import sys, os
import csv, json, simplejson

#input_file = sys.argv[1]

def getMesh(term):
    qString = """ 
                  PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                  PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                  SELECT *
                  FROM <http://id.nlm.nih.gov/mesh>
                  
                  WHERE {
                    
                  ?d rdfs:label ?dName .
                  FILTER(REGEX(?dName,"%s","i"))
                  
                  }
                  ORDER BY ?d """ % (term)
                  
    sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
    sparql.setQuery(qString)
    sparql.setReturnFormat(JSON)
    res = sparql.query().convert()
    return res


