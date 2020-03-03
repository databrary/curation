import sys
import os
import json
from utils import dbapi
import logging

BASE_DIR = os.path.dirname(os.path.abspath('../'))
CONFIG_DIR = os.path.join(BASE_DIR, 'config',)
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

if __name__ == '__main__':
    with open(os.path.join(CONFIG_DIR, 'credentials.json')) as creds:
        __credentials = json.load(creds)
        __username = __credentials['username']
        __password = __credentials['password']
        if __credentials is None:
            sys.exit()
        try:
            api = dbapi.DatabraryApi(__username, __password)
        except AttributeError as e:
            sys.exit()

    slots = api.get_volume_assets(874)
    for slot in slots:
        for asset in slot['assets']:
            # file_name = api.get_file_info(asset['id'])['name']
            # print(file_name)
            # print("Changing asset " + str(asset['id']) + " permission")
            response = api.post_file_permission(asset['id'], 2)
            logger.info(response)
            # print(file_name)

    # response = api.post_file_permission(219713, 0)
    # logger.info(response)
    api.logout()