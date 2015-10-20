import requests
from lxml import html
import csv, json
import time

BASE = 'https://www.nlm.nih.gov'
HOME = 'https://www.nlm.nih.gov/mesh/trees.html'

'''only the categories we want, with their order on the home page'''
category_map = {
    "Anatomy" : ("A", 1),
    "Organisms" : ("B", 2),
    "Analytical, Diagnostic and Therapeutic Techniques and Equipment Category": ("E", 5),
    "Psychiatry and Psychology" : ("F", 6),
    "Phenomena and Processes" : ("G", 7),
    "Disciplines and Occupations": ("H", 8),
    "Anthropology,Education,Sociology and Social Phenomena" : ("I", 9),
    "Information Science" : ("L", 12),
    "Named Groups" : ("M", 13), 
    "Health Care" : ("N", 14),
    "Publication Characteristics" : ("V", 15)
}


def get_page_tree(url):
    page = requests.get(url)
    return html.fromstring(page.text)

def save_all(data):
    with open("./data/mesh_terms.csv", 'wt') as f:
        w = csv.writer(f)
        for d in data:
            w.writerow(d)

def getdID(treeNum):
    _base = "http://id.nlm.nih.gov/mesh/sparql"
    _q = (
        
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
        "PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#> "
        "SELECT ?d "
        "FROM <http://id.nlm.nih.gov/mesh> "
        "WHERE {{ "
        "?d a meshv:Descriptor ."
        "?d meshv:treeNumber ?q ."
        "?q rdfs:label '{0}'@en"
        "}}"   
    ).format(treeNum)
    _inference = "true"
    _format = "JSON"     
    params = {"query":_q,
              "format": _format,
              "inference": _inference}
    res = requests.get(url=_base, params=params)
    sc = res.status_code
    print sc
    if sc == 200:
        data = json.loads(res.text)
        dId = data['results']['bindings'][0]['d']['value']
    else:
        print "whoops: %s" % res.status
        dId = "could not get"
    return dId


def get_category_links(d):
    rows = []
    rows.append(["category", "topic", "tree_header", "term", "tree_number"])
    tree = get_page_tree(HOME)
    for k,v in d.items():
        _xpath_base = '//div[@id="body"]/ol/li[%s]/' % (v[1])
        _xpath_li = _xpath_base + 'ul/li/text()'
        topics = [x for x in tree.xpath(_xpath_li) if x != ' '] 
        count = 0 
        for i in topics:
            topic, tree_head = i.split(' [')
            tree_head = tree_head.strip()[:-1]
            _xpath_a = _xpath_base + 'ul/li[%s]/a[1]/@href' % (str(int(topics.index(i))+1))
            link = BASE + tree.xpath(_xpath_a)[0]
            term_html = get_page_tree(link)
            terms = term_html.xpath('//div[@id="body"]//li/a/text()')
            for t in terms:
                term, treeNum = t.split(' [')
                treeNum = treeNum[:-1]
                dID = getdID(treeNum)
                r = [k, topic, tree_head, term, treeNum, dID]
                count += 1
                print count, "adding: ", r
                rows.append(r)
                if count == 300:
                    count = 0    
                    time.sleep(40) #this is probably excessive, the limit is 500 requests a minute
    save_all(rows)            

if __name__ == '__main__':
    get_category_links(category_map)