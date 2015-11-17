#!/usr/bin/env python2.7

import sys, os
import json
import argparse
import psycopg2
from config import conn as c 
import requests
from pprint import pprint

_QUERIES = {
    "db_volumes":"select v.id, volume_creation(v.id), v.name, owners, v.body from volume v left join volume_owners o ON v.id = o.volume where v.id > 3 order by v.id;",
    "op_parties":"select wp.id, wp.subject, cv.* from work_packages wp left join custom_values cv on cv.customized_id = wp.id where cv.customized_type = 'WorkPackage' and wp.type_id = 6 and wp.project_id = 12 and cv.custom_field_id = 29 order by wp.id asc;",
    "op_workpackages": "select wp.id, wp.type_id, wp.project_id, wp.parent_id, wp.category_id, wp.created_at, wp.start_date, cv.* from work_packages wp left join custom_values cv on cv.customized_id = wp.id where cv.customized_type = 'WorkPackage' and project_id = 14 and cv.custom_field_id = 29 order by wp.id asc;"
}

class DB(object):
    _conn = None
    _cur = None

    def __init__(self, host, database, user, password, port):
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._port = port
        self._conn = psycopg2.connect(host=self._host, database=self._database, user=self._user, password=self._password, port=self._port)
        self._cur = self._conn.cursor()

    def __del__(self):
        return self._conn.close()        

    def query(self, query, params=None):
        self._cur.execute(query, params)
        return self._cur.fetchall()

def wp_vols(data):
    return sorted([d[11] for d in data if d[11] != None and d[11] != ''], key=lambda x: float(x))

def compare(op_vols, db_vols):
    return [z for z in db_vols if str(z[0]) not in op_vols]

def getData(vol_data, party_data):
    nl = []
    for v in vol_data:
        d = {}
        owner_id = v[3][0].split(':')[0] if v[3] is not None else None
        if owner_id is not None:
            parent_id = [p[0] for p in party_data if p[6]==owner_id]
        else:
            parent_id = None
        
        d["owner_id"] = owner_id
        d["parent_id"] = parent_id
        d["volume_id"] = v[0]
        d["start_date"] = v[1]
        d["title"] = v[2]

        nl.append(d)
    return nl

def prepareData(data):
    fresh_data = []
    for i in data:
        record = {
        "customField37": True,
        "_links": {
            "type": {"href":"project/api/v3/types/16"},
            "status":{"href":"project/api/v3/statuses/1"},
            "priority":{"href":"project/api/v3/priorities/3"}
            }
        }
        if type(i['parent_id']) == list:
            if i['parent_id'] != []:
                pid = int(i['parent_id'][0])
            else:
                pid = None
        else:
            pid = None
        
        record['subject'] = i['title']
        record['start_date'] = i['start_date'].strftime('%Y-%m-%d')
        record['parentId'] = pid
        record['customField29'] = int(i['volume_id'])
        fresh_data.append(record)

    return fresh_data

if __name__ == '__main__':
    db_DB = DB(c.db['HOST'], c.db['DATABASE'], c.db['USER'], c.db['PASSWORD'], c.db['PORT'])
    op_DB = DB(c.op['HOST'], c.op['DATABASE'], c.op['USER'], c.op['PASSWORD'], c.op['PORT'])
    
    #
    # 1 go to dbrary and get all volumes (id, owner id)
    #
    db_volumes = db_DB.query(_QUERIES['db_volumes'])
    #
    # 2 get all wp from op for the volumes project with volume id
    #   
    op_workpackages = op_DB.query(_QUERIES['op_workpackages'])
    #   - index the volumes in already
    volumes_in_op = wp_vols(op_workpackages)
    
    #
    # 3 compare data and determine all of the volumes in dbrary that need to be added
    #
    vols_to_add = compare(volumes_in_op, db_volumes)
    
    #
    # 4 prepare data for adding to wp
    #   - get user information same way as get volume info from wp as #2
    op_parties = op_DB.query(_QUERIES['op_parties'])
    #print op_parties 
    raw_data = getData(vols_to_add, op_parties)
    ready_data = prepareData(raw_data)
    # 
    pprint(ready_data)
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