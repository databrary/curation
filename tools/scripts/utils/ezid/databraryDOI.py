import ezid_api
import psycopg2
from config import conn as c

try:
	conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s' % (c._DEV_CREDENTIALS['db'], 
																	   c._DEV_CREDENTIALS['u'], 
																	   c._DEV_CREDENTIALS['host'], 
																	   c._DEV_CREDENTIALS['p']))
except:
	print("Unable to connect to the database")

cur = conn.cursor()

try:
    cur.execute("""SELECT * FROM volume""")
except:
    print("Query failed")

rows = cur.fetchall()

print('here is what you requested')
print(rows)