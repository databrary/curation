import ezid_api
import logging #need to make use of this over printing
import psycopg2
import hashlib
from lxml import etree as e
from config import conn as c
import datacite_validator as dv
import datetime

target_path = "https://example.org"


sql = {'QueryAll' : ("SELECT v.id as target, volume_creation(v.id), v.name as title, COALESCE(sortname || ', ', '') || prename as creator, p.id as party_id, va1.individual as access "
            "FROM volume_access va1 "
            "JOIN ("
            "SELECT DISTINCT volume "
            "FROM volume_access va "
            "WHERE (va.party = 0 AND va.individual = 'SHARED') OR (va.party = -1 AND va.individual = 'PUBLIC') "
            ") va2 USING (volume) "
            "INNER JOIN volume v ON v.id = va1.volume "
            "INNER JOIN party p ON p.id = va1.party "
            "WHERE va1.individual = 'ADMIN' "
            "ORDER BY target;"
            ), 
       'GetCitations' : "SELECT * FROM volume_citation WHERE volume IN (%s)",
       'GetPublished' : "SELECT * FROM volume_creation(%s)",
       'GetFunders' : "SELECT vf.volume, vf.awards, f.name, f.fundref_id FROM volume_funding vf LEFT JOIN funder f ON vf.funder = f.fundref_id WHERE volume IN (%s)"}

def __makeHash(record:dict) -> str:
	return hashlib.sha256(str(record).encode('UTF-8')).hexdigest()

def __compareHash(record:dict, existing:str) -> bool:
	return _makeHash(record) == existing

#wrap the connection in an object 
def makeConnection():
	try:
		conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], c._DEV_CREDENTIALS['u'], c._DEV_CREDENTIALS['host'], c._DEV_CREDENTIALS['p']))
	except Exception as e:
		print("Unable to connect to database. Exception: %s" % str(e), file=sys.stderr) 

	return conn.cursor()

def queryAll(cursor) -> list:
    try:
        cursor.execute(sql['QueryAll'])
    except Exception as e:
        print("Query for everything failed. Exception: %s" % str(e), file=sys.stderr)
    rows = cursor.fetchall()
    return rows

def _getCreators(rs:list) -> dict:
    '''compile all admin for a volume into a list of creators per volume'''
    creators = {r[0]:[] for r in rs}
    for r in rs:
        creators[r[0]].append(r[3])
    return creators

def _getCitations(cursor, vs:list) -> dict:
    try:
        cursor.execute(sql['GetCitations'] % vs)
    except Exception as e:
        print("Query for citations failed: ", e)
    citations = cursor.fetchall()
    citation_data = {}
    for c in citations:
        citation_data[c[0]] = {"cite_head":c[1], "cite_url":c[2], "cite_year":c[3]}
    return citation_data

def _getFunders(cursor, vs:list) -> dict:
    try:
        cursor.execute(sql['GetFunders'] % vs)
    except Exception as e:
        print("Query for funders failed: ", e)
    funders = cursor.fetchall()
    funder_data = {f[0]:[] for f in funders}
    for f in funders:
        funder_data[f[0]].append({"award_no":f[1], "funder":f[2], "fundref_id":f[3]})
    return funder_data

def _getPublished(cursor, v:int):
    try:
        cursor.execute(sql['GetPublished'] % v)
    except Exception as e:
        print("Query for published dates failed: ", e)
    published = cursor.fetchone()
    return str(published[0].year)

def _createXMLDoc(row:tuple, volume:str, creators:dict, funders:dict, citations:dict, publishedyr:str) -> str:
    '''taking in a row returned from the database, convert it to datacite xml
        according to http://ezid.cdlib.org/doc/apidoc.html#metadata-profiles this can
        be then sent along in the ANVL'''
    
    xmlns="http://datacite.org/schema/kernel-3"
    xsi="http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation="https://schema.datacite.org/meta/kernel-3/metadata.xsd"
    fundrefURI = "http://data.fundref.org/fundref/funder/"
    NSMAP = {None:xmlns, "xsi":xsi}
    xmldoc = e.Element("resource", attrib={"{"+xsi+"}schemaLocation":schemaLocation},  nsmap=NSMAP)
    ielem = e.SubElement(xmldoc, "identifier", identifierType="DOI")
    ielem.text = "(:tba)" #need to check on this, if there is already a DOI, put it here.
    pubelem = e.SubElement(xmldoc, "publisher")
    pubelem.text = "Databrary"
    pubyrelem = e.SubElement(xmldoc, "publicationYear")
    pubyrelem.text = publishedyr
    telem = e.SubElement(xmldoc, "titles")
    title = e.SubElement(telem, "title")
    title.text = row[2]
    reselem = e.SubElemetn(xmldoc, "resourceType" resourceTypeGeneral="Dataset")
    reselem.text = "Dataset"
    crelem = e.SubElement(xmldoc, "creators")
    felem = e.SubElement(xmldoc, "contributors")
    for c in creators[volume]:
        cr = e.SubElement(crelem, "creator")
        crname = e.SubElement(cr, "creatorName")
        crname.text = c
    if volume in funders.keys():
        for f in funders[volume]:   
            ftype = e.SubElement(felem, "contributor", contributorType="Funder")
            fname = e.SubElement(ftype, "contributorName")
            fname.text = f['funder']
            fid = e.SubElement(ftype, "nameIdentifier", schemeURI=fundrefURI, nameIdentifierScheme="FundRef")
            fid.text = fundrefURI + str(f['fundref_id'])
    if volume in citations.keys():
        cite_url = citations[volume]['cite_url']
        if cite_url is not None:
            relelem = e.SubElement(xmldoc, "relatedIdentifiers")
            relid = e.SubElement(relelem, "relatedIdentifier", relatedIdentifierType="URL", relationType="IsReferencedBy")
            relid.text = cite_url
    xmloutput = e.tostring(xmldoc, pretty_print=True, xml_declaration=True).decode('utf-8')  #will not need to decode if this is run on python 2.6. 
    xmltocheck = e.tostring(xmldoc).decode('utf-8')  #will not need to decode if this is run on python 2.6. 
    #dv._validateXML(xmltocheck) # this is not ideal because we have to send a (:tba) to ezid, even though that doesn't validate
    return xmloutput

def makeMetadata(cursor, rs:list) -> list:
    metafull = []
    target_base = target_path + "/volume/"
    volumes = ", ".join(list(set([str(r[0]) for r in rs])))
    citations = _getCitations(cursor, volumes)
    funders = _getFunders(cursor, volumes)
    creators = _getCreators(rs)
    for r in rs:
        vol = r[0]
        publishedyr = _getPublished(cursor, vol)
        xml = _createXMLDoc(r, vol, creators, funders, citations, publishedyr)
        metafull.append({"_target": target_base + str(vol), 
                          "_profile": "datacite", 
                          "_status": "reserved", 
                          "datacite": xml
                        })
    #dedupe records (since there's one row for every owner on the volume)
    mdPayload = []
    for m in metafull:
        if m not in mdPayload:
            mdPayload.append(m)
    
    return mdPayload

def postData(payload:list):
    ezid_doi_session = ezid_api.ApiSession(scheme='doi')
    for p in payload:
        print("now sending %s" % p)
        ezid_doi_session.mint(p)

if __name__ == "__main__":
    cur = makeConnection()
    rows = queryAll(cur)
    tosend = makeMetadata(cur, rows)
    postData(tosend)


'''TODOS:
    - Logging
    - wrap db connection in object: http://programmers.stackexchange.com/questions/200522/how-to-deal-with-database-connections-in-a-python-library-module
    - Make sure we're checking for all available and all records with DOIs (if has DOI but not available, need to change status to UNAVAILABLE)
    - Fallback logic for it cannot connect to db or ezid
    - Fallback logic if data fails to post
'''