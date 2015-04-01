import ezid_api
import psycopg2
import hashlib
from config import conn as c

target_path = "https://example.org"


'''Querying and creating DOIs for Databrary resources. 
   Relevant fields for sending to datacite:
   		datacite.title: <volume name>
   		datacite.publisher: Databrary
   		datacite.creator: <party name(s)> (who is a "creator")
   		datacite.publicationyear (when shared?)
   		datacite.type: Dataset'''

sqlQuery = ("SELECT v.id as target, v.name as title, COALESCE(prename || ' ', '') || sortname as creator, p.id as party_id, va1.individual as access "
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

def _makeHash(record:dict) -> str:
	return hashlib.sha256(str(record).encode('UTF-8')).hexdigest()

def _compareHash(record:dict, existing:str) -> bool:
	return _makeHash(record) == existing

def makeConnection():
	try:
		conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], c._DEV_CREDENTIALS['u'], c._DEV_CREDENTIALS['host'], c._DEV_CREDENTIALS['p']))
	except:
		conn = "Unable to connect to the database"

	return conn.cursor()

def queryAll(cursor) -> list:
    try:
        cursor.execute(sqlQuery)
    except:
        print("Query failed")
    rows = cursor.fetchall()
    return rows

def getCreators(rs:list) -> dict:
    '''compile all admin for a volume into a list of creators per volume'''
    creators = {r[0]:[] for r in rs}
    for r in rs:
        creators[r[0]].append(r[2])
    return creators


def makeMetadata(rs:list) -> list:
    mdPayload = []
    target_base = target_path + "/volume/"
    creators = getCreators(rs)
    for r in rs:
        '''check parity here'''
        mdPayload.append({"_target": target_base + str(r[0]), 
                          "_profile": "datacite", 
                          "_status": "reserved", 
                          "datacite.publisher":"Databrary", 
                          "datacite.title":r[1], 
                          "datacite.creator":('; ').join(creators[r[0]])
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


