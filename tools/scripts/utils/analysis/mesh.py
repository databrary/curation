import requests
from urllib import urlencode
import sys, os
import csv, json

'''
This script takes a list of terms from a csv file and searches for a match for that term 
in NLM MeSH (using the MeSH SPARQL endpoint @ http://id.nlm.nih.gov/mesh/sparql. 
Currently matching is rather immature and could definitely be enhanced.

'''

_INPUT_FILE = sys.argv[1]

def _checkPlural(term):
    '''needs more re. this is some really cheap evaluation for plurality, 
    which can be made more complicated in the future'''
    return term[-1] == 's'

def _formatPlural(term):
    sing = term[:-1]
    orig = term
    tmp = list(term)
    tmp[-1] = "(s?)"
    out = "".join(tmp)
    return (out, orig, sing)

def getMesh(term):
    _base = "http://id.nlm.nih.gov/mesh/sparql"
    _q = (
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
        "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> "
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "
        "PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#> "
        "PREFIX mesh: <http://id.nlm.nih.gov/mesh/> "
        "PREFIX mesh2015: <http://id.nlm.nih.gov/mesh/2015/> "
        "SELECT ?d ?cid ?concept ?note ?tnum "
        "FROM <http://id.nlm.nih.gov/mesh> "
        "WHERE {{ "
        "?d a meshv:Descriptor . "
        "?d meshv:concept ?cid . "
        "?d rdfs:label ?dName . "
        "?cid rdfs:label ?concept . "
        "?cid meshv:scopeNote ?note . "
        "?d meshv:treeNumber ?tnum . "
        "FILTER(REGEX(?dName,'{0}','i') || REGEX(?concept,'{0}','i')) " 
        "}} ORDER BY ?d"   
    ).format(term)
    _inference = "true"
    _format = "JSON"     
    params = {"query":_q,
              "format": _format,
              "inference": _inference}
    res = requests.get(url=_base, params=params)
    return res

def getTerms(cf):
    terms = {}
    with open(cf, 'rt') as f:
        d = csv.reader(f)
        h = next(d)
        for i in d:
            terms[i[0]] = i[1]
    return terms

def saveData(data):
    with open('./data/mesh.csv', 'wt') as f:
        out = csv.writer(f)
        head = ["termid", "term", "type", "cid", "did", "concept", "note", "tnumber"]
        out.writerow(head)
        for i in data:
            out.writerow(i)

def autoMatch(termid, term, evaluator, res):
    orig, sing = evaluator
    for r in res:
        cid = r['cid']['value']
        did = r['d']['value']
        concept = r['concept']['value']
        note = r['note']['value']
        tnum = r['tnum']['value']
        if concept.lower() == orig.lower():
            return [termid, term, "auto", cid, did, concept, note, tnum]
        elif sing is not None and concept.lower() == sing.lower():
            return [termid, term, "auto", cid, did, concept, note, tnum]
        elif res.index(r) < (len(res) - 1):
            continue
        else:
            return None

def evaluateChoices(termid, term, res):
    '''this function serves to:
        1) take a set of results back from the query,
        2) assign them a temporary id
        3) prints them to the console (conecept and note)
        4) takes user input to select which one 
        5) -or- sends back no match if there's no match
        6) returns a list of values to be inserted into the csv file'''
    inc = 1
    for r in res:
        r['choiceId'] = inc
        concept = r['concept']['value']
        note = r['note']['value']
        print ("%s) %s - %s" % (str(inc), concept, note))
        inc += 1

    selection = raw_input("Enter the number of your choice - if nothing fits, enter 99: ")
    
    if selection.isdigit():
        selection = int(selection)
    else:
        selection = 'NaN'    
    
    if selection == 99:
        return [termid, term, "manual", "NA", "NA", "NA", "NA", "NA"]
    elif selection == 'NaN':
        print("Please enter a number")
        evaluateChoices(res)
    elif selection > inc: 
        print("That option is not in the set of choices")
        evaluateChoices(res)
    else:
        for r in res:
            if r['choiceId'] == selection:
                record = r
        cid = record['cid']['value']
        did = record['d']['value']
        concept = record['concept']['value']
        note = record['note']['value']
        tnum = record['tnum']['value']
        return [termid, term, "manual", cid, did, concept, note, tnum]
    print(res)
        

def prepResults(termid, term, evaluator, res):
    res = res['results']['bindings']
    match = autoMatch(termid, term, evaluator, res)
    if len(res) is 0:
        print("No Results - %s" % (evaluator[0]))
        return [termid, term, "auto", "", "", "", "", ""]
    elif match is not None:
        print("success - setting automatch on - %s" % (evaluator[0]))
        return match
    else:
        print("need to evaluate for - %s" % (evaluator[0]))
        return evaluateChoices(termid, term, res)

def main(input_file):
        deposit = []
        terms = getTerms(input_file)
        for i,t in terms.items():
            orig = t
            sing = None
            if _checkPlural(t): 
                plural_set = _formatPlural(t)
                t, orig, sing = plural_set
            evaluator = (orig, sing)
            results = getMesh(t)
            data = json.loads(results.text)
            row = prepResults(i, t, evaluator, data)
            deposit.append(row)
        saveData(deposit)
    
if __name__ == '__main__':
    if _INPUT_FILE:
        main(_INPUT_FILE)
    else:
        print("You need to specify a csv with a list of terms.")
        sys.exit()


