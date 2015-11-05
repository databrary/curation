import urllib.request
import urllib.parse
from xml.dom import minidom

'''
This script searches the PubMed api based on a list of publications with DOIs. 
It returns the keywords and MeSH terms attached to that publication and adds 
those to the CSV file originally input.

'''

BASE_URL = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
SEARCH_PATH = 'esearch.fcgi?'
FETCH_PATH = 'efetch.fcgi?'

def fetchData(url):
    res = urllib.request.urlopen(url).read()
    xml = minidom.parseString(res)
    return xml

def getSearchResults(base, search_path, term, database="pubmed"):
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
                qual = meshHeadings[i].getElementsByTagName('QualifierName')
                desc = desc[0].childNodes[0].data if desc != [] else None
                qual = qual[0].childNodes[0].data if qual != [] else None
                if qual is not None:
                    mesh_results.append(desc+'--'+qual)
                else:
                    mesh_results.append(desc)
                               
        if keywords is not []:
            keyword_results = []
            for k in range(len(keywords)):
                keyw = keywords[k].childNodes[0].data
                keyword_results.append(keyw)

        return (mesh_results, keyword_results)




if __name__ == '__main__':
    import csv
    import sys, os

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
                results = getFullRecord(BASE_URL, FETCH_PATH, getSearchResults(BASE_URL, SEARCH_PATH, doi))
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






