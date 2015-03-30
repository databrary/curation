import ezid_api
import psycopg2
import hashlib
from config import conn as c


'''Querying and creating DOIs for Databrary resources. 
   Relevant fields for sending to datacite:
   		datacite.title: <volume name>
   		datacite.publisher: Databrary
   		datacite.creator: <party name(s)> (who is a "creator")
   		datacite.publicationyear (when shared?)
   		datacite.type: Dataset'''

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

def queryAll(cursor):
	try:
		#TODO: this query is for testing only.
	    cursor.execute("""SELECT volume.id as target, volume.name as title, party.name as creator FROM volume_access INNER JOIN volume ON volume_access.volume = volume.id INNER JOIN party ON volume_access.party = party.id WHERE volume_access.individual = 'ADMIN' GROUP BY target, creator ORDER BY target;""")
	except:
		print("Query failed")

	rows = cursor.fetchall()
	return rows

def makeMetadata(rows):
	mdPayload = []
	target_base = "https://example.org/volume/"
	for r in rows:
		'''check parity here'''
		mdPayload.append({"_target": target_base + str(r[0]), 
						  "_profile": "datacite", 
						  "_status": "reserved", 
						  "datacite.publisher":"exampleDB", 
						  "datacite.title":r[1][0:4], 
						  "datacite.creator":"Anonymous"
			})
	return mdPayload


def postData(payload):
	ezid_doi_session = ezid_api.ApiSession(scheme='doi')
	for p in payload:
		ezid_doi_session.mint(p)

if __name__ == "__main__":
	cur = makeConnection()
	rows = queryAll(cur)


