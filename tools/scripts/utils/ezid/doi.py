#!/usr/bin/python

import ezid_api
import logging
import psycopg2
from lxml import etree as e
#import datacite_validator as dv
import datetime
import sys, os
import getopt

opts, _ = getopt.getopt(sys.argv[1:], "l:ntU:P:d:u:p:")
LOG_DEST = None
NOMINT = False
TEST = False
EZID_USER = None
EZID_PASS = None
DATABASE = None
DATABASE_USER = None
DATABASE_PASS = None
for o, a in opts:
    if o == '-l':
        LOG_DEST = a
    elif o == '-n':
        NOMINT = True
    elif o == '-t':
        TEST = True
    elif o == '-U':
        EZID_USER = a
    elif o == '-P':
        EZID_PASS = a
    elif o == '-d':
        DATABASE = a
    elif o == '-u':
        DATABASE_USER = a
    elif o == '-p':
        DATABASE_PASS = a

#Initiate and configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if LOG_DEST:
    handler = logging.FileHandler(LOG_DEST)
else:
    handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

target_path = "https://databrary.org"
auth_num = "10.17910/B7"

sql = { 'QueryAll' : ("SELECT v.id as target, volume_creation(v.id), volume_access_check(v.id, -1) > 'NONE', v.name as title, "
            "owners as creator, doi, c.url, v.body "
            "FROM volume v "
            "LEFT JOIN volume_owners o ON v.id = o.volume "
            "LEFT JOIN volume_citation c ON v.id = c.volume "
            "WHERE v.id > 0 AND volume_access_check(v.id, -1) > 'NONE' OR doi IS NOT NULL "
            "ORDER BY target"
            ), 
       'GetFunders' : "SELECT vf.volume, vf.awards, f.name, f.fundref_id FROM volume_funding vf LEFT JOIN funder f ON vf.funder = f.fundref_id WHERE volume = %s", 
       'AddDOI' : "UPDATE volume SET doi = %s WHERE id = %s AND doi IS NULL"}

class dbDB(object):
    _conn = None
    _cur = None

    def __init__(self):
        self._conn = psycopg2.connect(host="localhost", database=DATABASE, user=DATABASE_USER, password=DATABASE_PASS)
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

def _getFunders(db, v): #v is a single volume id -> list
    db.query(sql['GetFunders'], (v,))
    funders = db._cur.fetchall()
    funder_data = []
    if len(funders) > 0:
        for f in funders:
            funder_data.append({"award_no":f[1], "funder":f[2], "fundref_id":f[3]})
    return funder_data

def _addDOI(db, new_doi):
    '''takes a dict with doi and the volume it belongs to and updates the database with those values'''
    params = (new_doi['doi'], new_doi['vol'])
    db.insert(sql['AddDOI'], params)
    db._conn.commit()

def _createXMLDoc(row, volume, funders, doi=None): #tuple, str, list, str -> xml str
    '''taking in a row returned from the database, convert it to datacite xml
        according to http://ezid.cdlib.org/doc/apidoc.html#metadata-profiles this can
        be then sent along in the ANVL'''
    vol_date = row[1]
    vol_title = row[3].decode('utf-8') if row[3] is not None else "(:unav)"
    cite_url = row[6]
    vol_body = row[7].decode('utf-8') if row[7] is not None else "(:unav)"
    xmlns="http://datacite.org/schema/kernel-3"
    xsi="http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation="http://datacite.org/schema/kernel-3 http://schema.datacite.org/meta/kernel-3/metadata.xsd"
    fundrefURI = "http://data.fundref.org/fundref/funder/"
    NSMAP = {None:xmlns, "xsi":xsi}
    xmldoc = e.Element("resource", attrib={"{"+xsi+"}schemaLocation":schemaLocation},  nsmap=NSMAP)
    ielem = e.SubElement(xmldoc, "identifier", identifierType="DOI")
    ielem.text = "(:tba)" if doi is None else doi
    pubelem = e.SubElement(xmldoc, "publisher")
    pubelem.text = "Databrary"
    pubyrelem = e.SubElement(xmldoc, "publicationYear")
    pubyrelem.text = str(vol_date.year) if vol_date is not None else "(:unav)"
    telem = e.SubElement(xmldoc, "titles")
    title = e.SubElement(telem, "title")
    title.text = vol_title
    reselem = e.SubElement(xmldoc, "resourceType", resourceTypeGeneral="Dataset")
    reselem.text = "Dataset"
    descelem = e.SubElement(xmldoc, "descriptions")
    description = e.SubElement(descelem, "description", descriptionType="Abstract")
    description.text = vol_body if vol_body is not None else "(:unav)"
    crelem = e.SubElement(xmldoc, "creators")
    felem = e.SubElement(xmldoc, "contributors")
    if row[4]:
        for c in row[4]:
            cr = e.SubElement(crelem, "creator")
            crname = e.SubElement(cr, "creatorName")
            crname.text = c.decode('utf-8').split(':', 1)[1]
    if len(funders) > 0:
        for f in funders:   
            ftype = e.SubElement(felem, "contributor", contributorType="Funder")
            fname = e.SubElement(ftype, "contributorName")
            fname.text = f['funder'].decode('utf-8')
            fid = e.SubElement(ftype, "nameIdentifier", schemeURI=fundrefURI, nameIdentifierScheme="FundRef")
            fid.text = fundrefURI + str(f['fundref_id'])
    if cite_url:
        if cite_url.startswith('doi:'):
            cite_url = "http://dx.doi.org/" + cite_url.split(':', 1)[1]
        relelem = e.SubElement(xmldoc, "relatedIdentifiers")
        relid = e.SubElement(relelem, "relatedIdentifier", relatedIdentifierType="URL", relationType="IsSupplementTo")
        relid.text = cite_url
    xmloutput = e.tostring(xmldoc)
    #dv._validateXML(xmloutput) # this is not ideal because we have to send a (:tba) to ezid, even though that doesn't validate
    return xmloutput

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
    volumes = [r[0] for r in rs]
    for r in rs:
        vol = r[0]
        shared = r[2]
        vol_doi = r[5]
        funders = _getFunders(db, vol)
        if shared:
            status = "public"
            if vol_doi:
                xml = _createXMLDoc(r, vol, funders, vol_doi)
                allToUpload['modify'].append({'_id':"doi:"+vol_doi, 'record':_generateRecord(status, xml, vol)})
            else:
                xml = _createXMLDoc(r, vol, funders)
                allToUpload['mint'].append({"volume":vol, "record":_generateRecord(status, xml, vol)})
        elif vol_doi:
                status = "unavailable"
                allToUpload['modify'].append({'_id':"doi:"+vol_doi, 'record':_generateRecord(status, '', vol)})

    mdPayload = {'mint':_payloadDedupe(allToUpload, 'mint'), "modify":_payloadDedupe(allToUpload, 'modify')}
    return mdPayload

def postData(db, payload):
    global EZID_USER, EZID_PASS
    if not EZID_USER:
        db.query("SELECT username, password FROM ezid_account")
        (EZID_USER, EZID_PASS) = db._cur.fetchone()
    ezid_doi_session = ezid_api.ApiSession(username=EZID_USER, password=EZID_PASS, scheme='doi', naa=auth_num)
    #check if the server is up, if not, bail
    server_response = ezid_doi_session.checkserver()
    if server_response == True:
    	logger.info('ezid server is up, starting operation')
    else:
    	logger.info('ezid server seems to be down, exiting since will not be able to do anything until it comes back up')
    	sys.exit()
    logger.info('minting %s DOIs and modifiying %s existing records' % (str(len(payload['mint'])), str(len(payload['modify']))))
    #start by minting any new shares
    for p in payload['mint']:
        volume = p['volume']
        record = p['record']
        if NOMINT == True:
            mint_res = "Your DOI for %s will not be minted because this is test mode" % volume
        else:
            mint_res = ezid_doi_session.mint(record)
        if mint_res.startswith('doi'):
            curr_doi = mint_res.split('|', 1)[0].strip().split(':', 1)[1]
            new_doi = {'vol':volume, 'doi':curr_doi}
            _addDOI(db, new_doi)
            logger.info('minted doi: %s for volume %s' % (curr_doi, volume))
        else:
            logger.error('something went wrong minting a DOI for volume %s, error returned: %s' % (volume, mint_res))
    #next update existing records with dois
    for q in payload['modify']:
        identifier = q['_id']
        record = q['record']
        new_status = record['_status']
        mod_res = ezid_doi_session.recordModify(identifier, record)
        if type(mod_res) == dict:
            logger.info('%s successfully modified' % identifier)
        elif mod_res.startswith('error'):
            logger.error('something went wrong modifying a record for DOI: %s, error returned: %s' % (identifier, mod_res))

if __name__ == "__main__":
    db = dbDB()
    rows = queryAll(db)
    tosend = makeMetadata(db, rows)
    if TEST:
        print(tosend)
    else:
        postData(db, tosend)
    del db
