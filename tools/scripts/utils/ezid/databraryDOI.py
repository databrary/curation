import ezid_api
import logging #TODO: replace all prints with this
import psycopg2
from lxml import etree as e
from config import conn as c
import datacite_validator as dv
import datetime
import sys


'''TODOS:
    - Logging
    - Fallback logic for it cannot connect to db or ezid
    - Fallback logic if data fails to post
'''

target_path = "http://databrary.org"

sql = { 'QueryAll' : ("SELECT v.id as target, volume_creation(v.id), volume_access_check(v.id, -1) > 'NONE', v.name as title, "
            "COALESCE(sortname || ', ' || prename, sortname, '') as creator, p.id as party_id, volume_doi.doi, volume_citation.* "
            "FROM volume v "
            "LEFT JOIN volume_access va1 ON v.id = va1.volume AND va1.individual = 'ADMIN' "
            "JOIN party p ON p.id = va1.party "
            "LEFT JOIN volume_doi ON v.id = volume_doi.volume "
            "LEFT JOIN volume_citation ON v.id = volume_citation.volume "
            "ORDER BY target;"
            ), 
       'GetFunders' : "SELECT vf.volume, vf.awards, f.name, f.fundref_id FROM volume_funding vf LEFT JOIN funder f ON vf.funder = f.fundref_id WHERE volume IN %s;", 
       'AddDOI' : "INSERT into volume_doi VALUES (%s, %s)"}

class dbDB(object):
    _conn = None
    _cur = None

    def __init__(self):
        try:
            self._conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], c._DEV_CREDENTIALS['u'], c._DEV_CREDENTIALS['host'], c._DEV_CREDENTIALS['p']))
        except Exception as e:
            sys.stderr.write("Unable to connect to database. Exception: %s" % str(e))
        self._cur = self._conn.cursor()

    def __del__(self):
        return self._conn.close()

    def query(self, query, params=None):
        return self._cur.execute(query, params)
        

    def insert(self, insert, params=None):
        return self._cur.execute(insert, params)

def queryAll(db):
    db.query(sql['QueryAll'])
    return db._cur.fetchall()

def _getFunders(db, vs): #vs is a tuple of volume ids -> dict
    db.query(sql['GetFunders'], (vs,))
    funders = db._cur.fetchall()
    funder_data = {f[0]:[] for f in funders}
    for f in funders:
        funder_data[f[0]].append({"award_no":f[1], "funder":f[2], "fundref_id":f[3]})
    return funder_data

def _addDOIS(db, new_dois):
    '''takes a list of dicts with dois and the volumes they belong to and updates the database with those values'''
    for i in new_dois:
        params = (i['vol'], i['doi'])
        db.insert(sql['AddDOI'], params)
    db._conn.commit()

def _createXMLDoc(row, volume, creators, funders, doi=None): #tuple, str, dict, dict, dict, str, -> xml str
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
    ielem.text = "(:tba)" if doi is None else doi
    pubelem = e.SubElement(xmldoc, "publisher")
    pubelem.text = "Databrary"
    pubyrelem = e.SubElement(xmldoc, "publicationYear")
    pubyrelem.text = str(row[1].year) if row[1] is not None else "(:unav)"
    telem = e.SubElement(xmldoc, "titles")
    title = e.SubElement(telem, "title")
    title.text = row[3].decode('utf-8')
    reselem = e.SubElement(xmldoc, "resourceType", resourceTypeGeneral="Dataset")
    reselem.text = "Dataset"
    crelem = e.SubElement(xmldoc, "creators")
    felem = e.SubElement(xmldoc, "contributors")
    for c in creators[volume]:
        cr = e.SubElement(crelem, "creator")
        crname = e.SubElement(cr, "creatorName")
        crname.text = c.decode('utf-8')
    if volume in funders.keys():
        for f in funders[volume]:   
            ftype = e.SubElement(felem, "contributor", contributorType="Funder")
            fname = e.SubElement(ftype, "contributorName")
            fname.text = f['funder'].decode('utf-8')
            fid = e.SubElement(ftype, "nameIdentifier", schemeURI=fundrefURI, nameIdentifierScheme="FundRef")
            fid.text = fundrefURI + str(f['fundref_id'])
    cite_url = row[9]
    if cite_url is not None:
        if cite_url.startswith('doi'):
            cite_url = "http://dx.doi.org/" + cite_url.split(':')[1]
        relelem = e.SubElement(xmldoc, "relatedIdentifiers")
        relid = e.SubElement(relelem, "relatedIdentifier", relatedIdentifierType="URL", relationType="IsSupplementTo")
        relid.text = cite_url
    xmloutput = e.tostring(xmldoc)
    #dv._validateXML(xmloutput) # this is not ideal because we have to send a (:tba) to ezid, even though that doesn't validate
    return xmloutput

def _getCreators(rs): #rs is a list of rows
    '''compile all admin for a volume into a list of creators per volume'''
    creators = {r[0]:[] for r in rs}
    for r in rs:
        creators[r[0]].append(r[4])
    return creators

def _generateRecord(status, xml, vol):
    target_base = target_path + "/volume/"
    record = {"_target": target_base + str(vol), 
                             "_profile": "datacite", 
                             "_status": status, 
                             "datacite": xml
                            }
    return record

def _payloadDedupe(records, record_kind):
    '''dedupe records (since there's one row for every owner on the volume)'''
    set_list = []
    for m in records[record_kind]:
        if m not in set_list:
            set_list.append(m)
    return set_list

def makeMetadata(db, rs): #rs is a list -> list of metadata dict
    allToUpload = {"mint":[], "modify":[]}
    volumes = tuple(set([r[0] for r in rs]))
    funders = _getFunders(db, volumes)
    creators = _getCreators(rs)
    for r in rs:
        vol = r[0]
        shared = r[2]
        vol_doi = r[6]
        if shared is True and vol_doi is None:
            status = "public"
            xml = _createXMLDoc(r, vol, creators, funders)
            allToUpload['mint'].append({"volume":vol, "record":_generateRecord(status, xml, vol)})
        elif shared is not True and vol_doi is not None:
            status = "unavailable"
            xml = _createXMLDoc(r, vol, creators, funders, vol_doi)
            allToUpload['modify'].append({'_id':"doi:"+vol_doi, 'record':_generateRecord(status, xml, vol)})
        elif shared is True and vol_doi is not None:
            status = "public"
            xml = _createXMLDoc(r, vol, creators, funders, vol_doi)
            allToUpload['modify'].append({'_id':"doi:"+vol_doi, 'record':_generateRecord(status, xml, vol)})

    mdPayload = {'mint':_payloadDedupe(allToUpload, 'mint'), "modify":_payloadDedupe(allToUpload, 'modify')}
    return mdPayload

def postData(db, payload):
    new_dois = []
    ezid_doi_session = ezid_api.ApiSession(scheme='doi')
    for p in payload['mint']:
        volume = p['volume']
        record = p['record']
        print "now minting %s" % record
        mint_res = ezid_doi_session.mint(record)
        if mint_res.startswith('doi'):
            curr_doi = mint_res.split('|')[0].strip().split(':')[1]
            print "the doi for volume %s is: %s" % (volume, curr_doi)
            new_dois.append({'vol':volume, 'doi':curr_doi})
        else:
            print "something appears to have gone wrong, check the script log"
    _addDOIS(db, new_dois)

    for q in payload['modify']:
        identifier = q['_id']
        record = q['record']
        print "now modifying %s" % q
        mod_res = ezid_doi_session.recordModify(identifier, record)
        #TODO: check response here and act accordingly

if __name__ == "__main__":
    db = dbDB()
    rows = queryAll(db)
    tosend = makeMetadata(db, rows)
    postData(db, tosend)
    del db