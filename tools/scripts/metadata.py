import psycopg2
from lxml import etree as e
import sys, os
from utils.config import conn as c

DATABASE = c._DEV_CREDENTIALS['db']
DATABASE_USER = c._DEV_CREDENTIALS['u']
DATABASE_PASS = c._DEV_CREDENTIALS['p']

sql = { 'VolumeMD' : ("SELECT v.id as target, volume_creation(v.id), volume_access_check(v.id, -1) > 'NONE', v.name as title, "
            "owners as creator, doi, c.url, v.body "
            "FROM volume v "
            "LEFT JOIN volume_owners o ON v.id = o.volume "
            "LEFT JOIN volume_citation c ON v.id = c.volume "
            "WHERE v.id > 0 AND volume_access_check(v.id, -1) > 'NONE' OR doi IS NOT NULL "
            "ORDER BY target"
            ),
        'VolumeAssets' : "select c.*, a.*, f.* from container c join slot_asset sa on c.id = sa.container join asset a on sa.asset = a.id join format f on a.format = f.id where c.volume = %s;"
      }

class dbClient(object):
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

def getVolMD(db):
    db.query(sql['VolumeMD'])
    return db._cur.fetchall()

if __name__ == '__main__':
    db = dbClient()
    vmd = getVolMD(db)
    print vmd