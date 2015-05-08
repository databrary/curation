import ezid_api
import psycopg2
import hashlib
from config import conn as c

target_path = "https://example.org"

sqlQueryAll = ("SELECT v.id as target, volume_creation(v.id), v.name as title, COALESCE(prename || ' ', '') || sortname as creator, p.id as party_id, va1.individual as access "
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
            ) 
sqlGetCitations = "SELECT * FROM volume_citation WHERE volume IN (%s)"
sqlGetFunders = "SELECT vf.volume, vf.awards, f.name FROM volume_funding vf LEFT JOIN funder f ON vf.funder = f.fundref_id WHERE volume IN (%s)"

def _makeHash(record:dict) -> str:
	return hashlib.sha256(str(record).encode('UTF-8')).hexdigest()

def _compareHash(record:dict, existing:str) -> bool:
	return _makeHash(record) == existing

def makeConnection():
	try:
		conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], c._DEV_CREDENTIALS['u'], c._DEV_CREDENTIALS['host'], c._DEV_CREDENTIALS['p']))
	except Exception as e:
		print("Unable to connect to database. Exception: %s" % str(e), file=sys.stderr) 

	return conn.cursor()

def queryAll(cursor) -> list:
    try:
        cursor.execute(sqlQueryAll)
    except Exception as e:
        print("Query for everything failed. Exception: %s" % str(e), file=sys.stderr)
    rows = cursor.fetchall()
    return rows

def getCreators(rs:list) -> dict:
    '''compile all admin for a volume into a list of creators per volume'''
    creators = {r[0]:[] for r in rs}
    for r in rs:
        creators[r[0]].append(r[2])
    return creators

def getCitations(cursor, vs:str) -> dict:
    try:
        cursor.execute(sqlGetCitations % vs)
    except Exception as e:
        print("Query for citations failed: ", e)
    citations = cursor.fetchall()
    citation_data = {}
    for c in citations:
        citation_data[c[0]] = {"cite_head":c[1], "cite_url":c[2], "cite_year":c[3]}
    return citation_data

def getFunders(cursor, vs:str) -> dict:
    try:
        cursor.execute(sqlGetFunders % vs)
    except Exception as e:
        print("Query for funders failed: ", e)
    funders = cursor.fetchall()
    funder_data = {f[0]:[] for f in funders}
    for f in funders:
        funder_data[f[0]].append({"award_no":f[1], "funder":f[2]})
    return funder_data

def makeMetadata(cursor, rs:list) -> list:
    mdPayload = []
    target_base = target_path + "/volume/"
    volumes = ", ".join(list(set([str(r[0]) for r in rs])))
    citations = getCitations(cursor, volumes)
    funders = getFunders(cursor, volumes)
    creators = getCreators(rs)
    for r in rs:
        '''check parity here'''

        #This is a sketch of the metadata, will probably need this to be reshaped in the final version
        mdPayload.append({"_target": target_base + str(r[0]), 
                          "_profile": "dc", 
                          "_status": "reserved", 
                          "dc.publisher":"Databrary",
                          "dc.date": r[1].strftime('%Y-%m-%d'), 
                          "dc.title":r[2], 
                          "dc.creator":('; ').join(creators[r[0]]),
                          "dc.citation": "{0}({1})".format(citations[r[0]]['cite_head'], citations[r[0]]['cite_year']) if r[0] in citations else None,
                          "dc.funder": "; ".join(str(f['funder'])+"-"+str(f['award_no']) for f in funders[r[0]]) if r[0] in funders else None
                        })
    return mdPayload


def postData(payload:list):
	ezid_doi_session = ezid_api.ApiSession(scheme='doi')
	for p in payload:
		print("I AM NOW SENDING THIS TO THE EZID SERVER [%s]: %s" % (ezid_doi_session, p))
    #ezid_doi_session.mint(p)

if __name__ == "__main__":
	print('What do you even want me to do with that?')
  #cur = makeConnection()
	#rows = queryAll(cur)


