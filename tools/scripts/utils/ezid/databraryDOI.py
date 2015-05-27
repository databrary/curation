import ezid_api
import logging #TODO: replace all prints with this
import psycopg2
from lxml import etree as e
from config import conn as c
import datacite_validator as dv
import datetime
import sys

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
       'GetFunders' : "SELECT vf.volume, vf.awards, f.name, f.fundref_id FROM volume_funding vf LEFT JOIN funder f ON vf.funder = f.fundref_id WHERE volume IN (%s);"}

#wrap the connection in an object 
def makeConnection():
	try:
		conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], c._DEV_CREDENTIALS['u'], c._DEV_CREDENTIALS['host'], c._DEV_CREDENTIALS['p']))
	except Exception as e:
		sys.stderr.write("Unable to connect to database. Exception: %s" % str(e))

	return conn.cursor()

def queryAll(cursor):
    try:
        cursor.execute(sql['QueryAll'])
    except Exception as e:
        sys.stderr.write("Query for everything failed. Exception: %s" % str(e))
    rows = cursor.fetchall()
    return rows

def _getCreators(rs): #rs is a list of rows
    '''compile all admin for a volume into a list of creators per volume'''
    creators = {r[0]:[] for r in rs}
    for r in rs:
        creators[r[0]].append(r[4])
    return creators

def _getFunders(cursor, vs): #vs is a list of volumes -> dict
    try:
        cursor.execute(sql['GetFunders'] % vs)
    except Exception as e:
        sys.stderr.write("Query for funders failed: ", e)
    funders = cursor.fetchall()
    funder_data = {f[0]:[] for f in funders}
    for f in funders:
        funder_data[f[0]].append({"award_no":f[1], "funder":f[2], "fundref_id":f[3]})
    return funder_data

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

def makeMetadata(cursor, rs): #rs is a list -> list of metadata dict
    allToUpload = {"mint":[], "modify":[]}
    volumes = ", ".join(list(set([str(r[0]) for r in rs])))
    funders = _getFunders(cursor, volumes)
    creators = _getCreators(rs)
    for r in rs:
        vol = r[0]
        shared = r[2]
        vol_doi = r[6]
        if shared is True and vol_doi is None:
            status = "public"
            xml = _createXMLDoc(r, vol, creators, funders)
            allToUpload['mint'].append(_generateRecord(status, xml, vol))
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

def postData(payload):
    ezid_doi_session = ezid_api.ApiSession(scheme='doi')
    for p in payload['mint']:
        print "now minting %s" % p
        mint_res = ezid_doi_session.mint(p)
        if mint_res.startswith('doi'):
            curr_doi = res.split('|')[0].strip().split(':')[1]
            print "the doi for this resource is: %s" % curr_doi
        else:
            print "something appears to have gone wrong, check the script log"
        #TODO: update database or store in datastructure to update after all done
    for q in payload['modify']:
        print "now modifying %s" % q
        mod_res = ezid_doi_session.recordModify(q['_id'], q['record'])
        #TODO: check response here and act accordingly

if __name__ == "__main__":
    cur = makeConnection()
    rows = queryAll(cur)
    tosend = makeMetadata(cur, rows)
    postData(tosend)


'''TODOS:
    - Logging
    - wrap db connection in object: http://programmers.stackexchange.com/questions/200522/how-to-deal-with-database-connections-in-a-python-library-module
    - Fallback logic for it cannot connect to db or ezid
    - Fallback logic if data fails to post
'''