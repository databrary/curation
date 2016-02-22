#!/usr/bin/env python2.7

'''script to fetch assisted curation assets from database
   and place them into a csv file for ingest'''
#system
import csv
import argparse
import os
import time
#project specific
from utils import dbclient
from utils.config import conn as c

parser = argparse.ArgumentParser(description='enter volume to get top level assets for that volume as provided through assisted curation')
parser.add_argument('-v', '--volume', help='Volume id for where the target files are located', required=True)
parser.add_argument('-p', '--path', help='Filepath for where to put csv output of fetch', required=True)
args = vars(parser.parse_args())

_VOL = args['volume']
_OUTPUT_PATH = args['path']
_CSV_FILE = '%s_assisted_curation_%s.csv' % (_VOL, str(int(time.time())))
_DESTINATION = os.path.join(_OUTPUT_PATH, _CSV_FILE)

_FETCH_QUERY = 'select a.*, c.id as container_id from asset a left join slot_asset sa on a.id = sa.asset left join container c on sa.container = c.id where a.volume = %s and c.top = true'

if __name__ == '__main__':
    db = dbclient.DB(c.db['HOST'], c.db['DATABASE'], c.db['USER'], c.db['PASSWORD'], c.db['PORT'])
    asset_query = _FETCH_QUERY % _VOL
    db.querytocsv(asset_query, _DESTINATION)
