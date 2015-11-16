#!/usr/bin/env python2.7

import sys, os
import json
import argparse
import psycopg2
from config import conn as c 

_QUERIES = {
    "db_volumes":"select * from volume;",
    "op_parties":"select wp.id, wp.subject, cv.* from work_packages wp left join custom_values cv on cv.customized_id = wp.id where cv.customized_type = 'WorkPackage' and wp.type_id = 6 and wp.project_id = 12 and cv.custom_field_id = 29 order by wp.id asc;"
}

class DB(object):
    _conn = None
    _cur = None

    def __init__(self, host, database, user, password):
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._conn = psycopg2.connect(host=self._host, database=self._database, user=self._user, password=self._password)
        self._cur = self._conn.cursor()

    def __del__(self):
        return self._conn.close()        

    def query(self, query, params=None):
        return self._cur.execute(query, params)

if __name__ == '__main__':
    db_DB = DB(c.db['HOST'], c.db['DATABASE'], c.db['USER'], c.db['PASSWORD'])
    op_DB = DB(c.op['HOST'], c.op['DATABASE'], c.op['USER'], c.op['PASSWORD'])
    
    #
    # 1 go to dbrary and get all volumes (id, owner id)
    #
    db_volumes = db_DB.query(_QUERIES['db_volumes'])
    
    #
    # 2 get all wp from op for the volumes project
    #   - get all from /project/api/experimental/projects/volumes/work_packages.json
    #   - index
    #   - grab individual from /project/api/v3/work_packages/{id}.json
    #   - need volume id 
    
    #
    # 3 compare data and determine all of the volumes in dbrary that need to be added
    #
    
    #
    # 4 prepare data for adding to wp
    #   - get user information same way as get volume info from wp as #2
    #       select wp.id, wp.subject, cv.* from work_packages wp left join custom_values cv on cv.customized_id = wp.id where cv.customized_type = 'WorkPackage' and wp.type_id = 6 and wp.project_id = 12 and cv.custom_field_id = 29 order by wp.id asc;
    op_parties = op_DB.query(_QUERIES['op_parties'])
    
    #   - volume title -> subject; parentId -> parentId; vid -> databrary id; creation date -> start date
    

    #   
    # 5 insert these records via the api (POST - /project/api/v3/projects/volumes/work_packages)
    # 
    
    # 
    # 6 what about edits? (later)
    # 
    
    # 
    # 7 close up data base, die 
    #      
    #      
    #      https://databrary.org/project/api/experimental/projects/tracking/work_packages.json?per_page=1000&filters=[{ "type_id": { "operator": 6, "values": null }" }]