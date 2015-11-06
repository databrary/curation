import urllib.request
import urllib.parse
from xml.dom import minidom

'''
This script searches the PubMed api based on a list of publications with DOIs. 
It returns the keywords and MeSH terms attached to that publication and adds 
those to the CSV file originally input.

It also, given a list of journals, will search for up to 1000 articles for each journal 
and spit out the mesh terms and keywords for each article if there are any.

'''

BASE_URL = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
SEARCH_PATH = 'esearch.fcgi?'
FETCH_PATH = 'efetch.fcgi?'
'''source for journal rankings: http://www.scimagojr.com/journalrank.php?area=3200&category=3204&country=all&year=2014&order=sjr&min=0&min_type=cd'''
JOURNALS = ["Educational Psychologist",
            "Current Directions in Psychological Science", 
            "Developmental Science",
            "Child Development",
            "Journal of child psychology and psychiatry, and allied disciplines"]

JOURNALS_TEST = ["Child Development"]

def fetchData(url):
    res = urllib.request.urlopen(url).read()
    xml = minidom.parseString(res)
    return xml

def getTermResults(base, search_path, term, database="pubmed"):
    params = {
        'db': database,
        'term': term,
    }
    url = base + search_path + urllib.parse.urlencode(params)
    xml = fetchData(url)
    
    if xml.getElementsByTagName('PhraseNotFound') != []:
        recordID = -999
    elif xml.getElementsByTagName('Id') == []:
        recordID = -9999
    else:
        recordID = xml.getElementsByTagName('Id')[0].childNodes[0].data
    
    return recordID

def getJournalResults(base, search_path, journals, database="pubmed"):
    '''e.g., http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1000&term=Current+Directions+in+Psychological+Science[Journal]+AND+journal+article[Publication%20Type]'''
    id_results = []
    for j in journals:
        journal_ids = {j:[]}
        jplus = j.replace(' ', '+')
        params = {
            'db': database,
            'retmax': 1000,
        } 
        term = '&term='+jplus+'[Journal]+AND+journal+article[Publication%20Type]'
        url = base + search_path + urllib.parse.urlencode(params) + term
        print(url)
        xml = fetchData(url)
        ids = xml.getElementsByTagName('Id')
        if ids is not []:        
            for i in range(len(ids)):
                articleId = ids[i].childNodes[0].data
                journal_ids[j].append(articleId)
        id_results.append(journal_ids)
    return id_results

def getFullRecord(base, fetch_path, recordID, retformat="xml", database="pubmed"):
    
    if recordID == -999 or recordID == -9999:
        return 0
    else:
        params = {
            'db': database,
            'id': recordID,
            'retmode': retformat
        }
        url = base + fetch_path + urllib.parse.urlencode(params)
        xml = fetchData(url)
        meshHeadings = xml.getElementsByTagName('MeshHeading')
        keywords = xml.getElementsByTagName('Keyword')
        
        if meshHeadings is not []:
            mesh_results = []
            for i in range(len(meshHeadings)):
                desc = meshHeadings[i].getElementsByTagName('DescriptorName')
                #qual = meshHeadings[i].getElementsByTagName('QualifierName')
                desctxt = desc[0].childNodes[0].data if desc != [] else None
                descid = desc[0].getAttribute('UI') if desc != [] else None
                #qual = qual[0].childNodes[0].data if qual != [] else None
                #if qual is not None:
                #    mesh_results.append({desc:})
                #else:
                mesh_dict = "%s|%s" % (desctxt,descid)
                mesh_results.append(mesh_dict)
                
                               
        if keywords is not []:
            keyword_results = []
            for k in range(len(keywords)):
                keyw = keywords[k].childNodes[0].data
                keyword_results.append(keyw)

        return (mesh_results, keyword_results)

if __name__ == '__main__':
    import csv
    import sys, os

    def doi_mesh():
    
        f = sys.argv[1]

        with open(f, 'rt') as c:
            reader = csv.reader(c)
            writer = csv.writer(open('./keyword_output.csv', 'wt'))
            header = next(reader)
            hindex = {header[i]: i for i in range(len(header))}
            header.extend(['mesh', 'keywords'])
            writer.writerow(header)
            doirow = hindex['doi']

            for row in reader:
                if row[doirow] != '':
                    doi = row[doirow].strip().replace('doi:', '')
                    results = getFullRecord(BASE_URL, FETCH_PATH, getTermResults(BASE_URL, SEARCH_PATH, doi))
                    if results != 0:
                        mesh = ";".join(results[0])
                        keyw = ";".join(results[1])
                        row.extend([str(mesh), str(keyw)])
                        writer.writerow(row)
                    else:
                        mesh = ""
                        keyw = ""
                        row.extend([str(mesh), str(keyw)])
                        writer.writerow(row)
                else:
                    mesh = ""
                    keyw = ""
                    row.extend([str(mesh), str(keyw)])
                    writer.writerow(row)

    def journal_mesh():
        
        writer = csv.writer(open('./journal_output.csv', 'wt'))
        head = ["journal", "mesh", "keywords"]
        jIds = getJournalResults(BASE_URL, SEARCH_PATH, JOURNALS)
        for i in jIds:
            for k,v in i.items():
                for j in v:
                    results = getFullRecord(BASE_URL, FETCH_PATH, j)
                    if results != 0:
                        mesh = ";".join(results[0])
                        keyw = ";".join(results[1])
                        writer.writerow([k, str(mesh), str(keyw)])

    if sys.argv[1] == "journals":
        journal_mesh()
    else:
        doi_mesh()







