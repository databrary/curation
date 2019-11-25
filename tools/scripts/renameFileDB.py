import sys
import logging
import os
import json
import hashlib
from utils import dbapi
from utils import csv_helpers as utils

# Run this SQL query on the server, replace VOLUME_ID by your volume id
# COPY (
#   SELECT
#       a.volume AS volume_id,
#       v.owners AS volume_owner,
#       sa.container AS session_id,
#       a.id AS asset_id,
#       a.sha1 AS sha1,
#       oa.sha1 AS origin_sha1,
#       t.origin AS origin_asset_id,
#   FROM slot_asset as sa
#       inner join asset a on sa.asset = a.id
#       inner join format f on a.format = f.id
#       left join transcode t on t.orig= oa.id
#       left join asset oa on t.orig = oa.id
#       left join volume_owners v on a.volume = v.volume
#   WHERE a.volume=VOLUME_ID) TO '/tmp/rename_asset.csv' WITH DELIMITER ',' CSV HEADER;

BASE_DIR = os.path.dirname(os.path.abspath('../'))
CONFIG_DIR = os.path.join(BASE_DIR, 'config',)
INPUT_DIR = os.path.join(BASE_DIR, 'tools', 'input')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')


logger = logging.getLogger('logs')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join(LOGS_DIR, 'all.log'))
ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

with open(os.path.join(CONFIG_DIR,'credentials.json')) as creds:
    __credentials = json.load(creds)
    __username = __credentials['username']
    __password = __credentials['password']
    if __credentials is None:
        logger.error('Cannot find Databrary credentials')
        sys.exit()
    try:
        api = dbapi.DatabraryApi(__username, __password)
    except AttributeError as e:
        logger.error(e)
        sys.exit()

def get_file_sha(file_path):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    file_path = os.path.realpath(file_path)
    file_sha = hashlib.sha1()
    with open(file_path, 'rb') as f:
        data = f.read(BUF_SIZE)
        while len(data) > 0:
            file_sha.update(data)
            data = f.read(BUF_SIZE)
    return file_sha.hexdigest()

def get_dir_sha(dir):
    dir_path = os.path.realpath(dir)
    files_sha_list = []
    logger.info("Looking for file in %s", INPUT_DIR)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            logger.info("Processing file %s", os.path.join(dir,file))
            files_sha_list.append({"name": api.getFileName(file), "sha1": get_file_sha(os.path.join(dir,file))})
    return files_sha_list

def get_server_sha(csv_name):
    sha_list = []
    csv_path = os.path.join(INPUT_DIR, csv_name)
    csv_reader = utils.giveMeCSV(csv_path)
    for row in csv_reader:
        sha = row['origin_sha1']
        if len(sha) > 0:
            sha_list.append({"asset_id": row["asset_id"], "sha1": sha[2:len(sha)]})
    return sha_list

def rename_server_asset(local_dir, server_sha_csv):
    local_sha_list = get_dir_sha(local_dir)
    server_sha_list = get_server_sha(server_sha_csv)
    for server_sha in server_sha_list:
        for local_sha in local_sha_list:
            if server_sha['sha1'] == local_sha['sha1']:
                api.post_file_name(server_sha['asset_id'], local_sha['name'])


if __name__ == '__main__':
    # Your CSV file must be inside input folder
    rename_server_asset(INPUT_DIR, 'rename_assets.csv')