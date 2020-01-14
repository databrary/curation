import sys
import argparse
import logging
import os
import re
import csv
import json
from utils import dbapi
from utils import csv_helpers as utils
from datetime import datetime
from dateutil.parser import parse

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

__session_headers_format = {
    "key": re.compile("^session-id"),
    "name": re.compile("^session-name"),
    "date": re.compile("^session-date"),
    "pilot": re.compile("^pilot-pilot"),
    "release": re.compile("^session-release"),
    "exclusion": re.compile("^exclusion[1-9]-reason"),  # exclusion1-reason,exclusion2-reason
    "tasks": re.compile("^task[1-9]-name"),  # task1-name,task2-name,task3-name
    "country": re.compile("^context-country"),
    "state": re.compile("^context-state"),
    "language": re.compile("^context-language"),
    "participantID": re.compile("participant-ID"),
    "setting": re.compile("^context-setting"),
    "group": re.compile("^group-name")
}

__participant_headers_format = {
    "participantID": re.compile("^participant-ID"),
    "birthdate": re.compile("^participant-birthdate"),
    "gender": re.compile("^participant-gender"),
    "race": re.compile("^participant-race"),
    "ethnicity": re.compile("^participant-ethnicity"),
    "language": re.compile("^participant-language"),
    "pregnancy term": re.compile("^participant-pregnancy term"),
    "disability": re.compile("^participant-disability"),
}

__db_formats = {
    "2": "csv",
    "4": "rtf",
    "5": "png",
    "6": "pdf",
    "7": "doc",
    "8": "odf",
    "9": "docx",
    "10": "xls",
    "11": "ods",
    "12": "xlsx",
    '13': "ppt",
    "14": "odp",
    "15": "pptx",
    "16": "opf",
    "18": "webm",
    "20": "mov",
    "-800": "mp4",
    "22": "avi",
    "23": "sav",
    "24": "wav",
    "19": "mpeg",
    "26": "chat",
    "-700": "jpeg",
    "21": "mts",
    "-600": "mp3",
    "27": "aac",
    "28": "wma",
    "25": "wmv",
    "29": "its",
    "30": "dv",
    "1": "txt",
    "31": "etf"
}

parser = argparse.ArgumentParser(
    description='Command line tool used to download the CSV format of a volume and generate session.csv and '
                'participants.csv needed for the ingest process')
parser.add_argument(
    '-f', '--file', help='Path to CSV File', type=str, required=False)
parser.add_argument(
    '-s', '--source', help='Volume ID source', type=int, dest='__source_volume_id', required=True)
parser.add_argument('-t', '--target',
                    help='Volume ID target', type=int, dest='__target_volume_id', required=True)

args = parser.parse_args()

with open(os.path.join(CONFIG_DIR,'credentials.json')) as creds:
    __credentials = json.load(creds)
    __username = __credentials['username']
    __password = __credentials['password']
    __superuser= __credentials['superuser']
    if __credentials is None:
        logger.error('Cannot find Databrary credentials')
        sys.exit()
    try:
        api = dbapi.DatabraryApi(__username, __password, __superuser)
    except AttributeError as e:
        logger.error(e)
        sys.exit()


def autoPrepCSV(source, target):
    """
    Fetch a volume content in CSV format
    """
    parseCSV(getCSV(source), source, target)


def parseCSV(file_path, source, target):
    """
    Parse Volume data found in the CSV file and generate data needed for a new Volume ingest, the method will
    generate a unique key for each session; composed of volume target id and session id. This key must match the
    session folder on the server. The function will download a list of assets in the source volume and generate a file path
    (on the server) for each asset
    e.g. target id 222 and session id 8888 the path on the server should be like this
    /nyu/stage/reda/222/2228888/asset_name.mp4
    :param file_path: CSV file path
    :param source: Volume ID
    :param target: New Volume ID
    :return:
    """

    csv_reader = utils.giveMeCSV(file_path)
    csv_headers = csv_reader.fieldnames

    sessions = []
    participants = []
    participants_headers = []
    sessions_headers = []
    for record in csv_reader:
        participant = {}
        session = {}
        for z in range(len(csv_headers)):
            for key, rx in __session_headers_format.items():
                match = rx.search(csv_headers[z])
                if match:
                    if key == 'key':
                        session_id = record[csv_headers[z]]
                        try:
                            session_assets = getSessionAssets(source, target, session_id)
                            session.update(session_assets)
                            for asset_key in session_assets.keys():
                                if asset_key not in sessions_headers:
                                    sessions_headers.append(asset_key)
                        except AttributeError as e:
                            logger.error(e.message)

                        session[key] = str(target) + session_id
                    elif key == 'date':
                        try:
                            date = parse(record[csv_headers[z]])
                            if isinstance(date, datetime):
                                session[key] = date.strftime("%m/%d/%Y")
                            else:
                                session[key] = record[csv_headers[z]]
                        except ValueError as e:
                            logger.error(e.message)
                    elif key == 'tasks' and key in session and record[csv_headers[z]] != '' and record[csv_headers[z]] is not None:
                        session.update(tasks=session[key] + ';' + record[csv_headers[z]])
                    else:
                        session[key] = record[csv_headers[z]]
                    if key not in sessions_headers:
                        sessions_headers.append(key)
            for key, rx in __participant_headers_format.items():
                match = rx.search(csv_headers[z])
                if match:
                    participant[key] = record[csv_headers[z]]
                    if key not in participants_headers:
                        participants_headers.append(key)

        sessions.append(session)
        participants.append(participant)
    writeCSV('sessions_' + str(target), sessions, sessions_headers)
    writeCSV('participants_' + str(target), participants, participants_headers)
    generateQuery(source, target)


def writeCSV(file_name, dict_data, headers):
    try:
        with open(os.path.join(INPUT_DIR, file_name + '.csv'), 'w') as csvfile:
            logger.info('Saving file %s in %s', file_name, INPUT_DIR)
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for data in dict_data:
                if any(field.strip() for field in data):
                    writer.writerow(data)

    except IOError as e:
        logger.error('I/O error %s', e.message)
    pass


def getCSV(source):
    return api.get_csv(source, INPUT_DIR)


def getFormat(format_id):
    return __db_formats.get(str(format_id), '')


def getSessionAssets(source, target, session):
    server_folder_path = '/nyu/stage/reda/' + str(target)
    try:
        assets = api.get_session_assets(source, session)

        new_assets = {}
        for i, asset in enumerate(assets):
            # Need to add clip_in here
            new_assets.update({'file_' + str(i + 1): server_folder_path + '/' + str(target) + str(session) + '/' \
                                                     + asset['name'] + '.' + getFormat(asset['format']),
                               'fname_' + str(i + 1): asset['name']})
            if getFormat(asset['format']) == 'mp4' \
                    or getFormat(asset['format']) == 'mp3' \
                    or getFormat(asset['format']) == 'mpeg' \
                    or getFormat(asset['format']) == 'avi' \
                    or getFormat(asset['format']) == 'mov':
                new_assets.update({'clip_in_' + str(i + 1): ''})

        return new_assets
    except AttributeError as e:
        logger.error(e.message)


def getVolumeSessions(source):
    try:
        sessions = api.get_sessions(source)
        return sessions
    except AttributeError as e:
        logger.error(e.message)


def getVolumeAssets(source, target):
    """
    Retrieve a list of assets and build a file path (On the server) for each asset.
    Important: Assets need to be copied to the /nyu staging folder, generated file paths need to be valid on the server
    otherwise the ingest will fail.
    :param source:
    :param target
    :return:
    """
    try:
        sessions = getVolumeSessions(source)

        for i, session in enumerate(sessions):
            logger.debug('Fetching session %d assets', session['id'])
            session['assets'] = getSessionAssets(source, target, int(session['id']))
            session['id'] = str(target) + str(session['id'])
            session['key'] = session.pop('id')
            sessions[i] = session

        return sessions
    except AttributeError as e:
        logger.error(e.message)


def generateQuery(source, target):
    """
    Generate Databrary DB query that
    :param source: Original Volume ID
    :param target: Target Volume ID
    :return:
    """
    logger.info("COPY (select 'mkdir -p /nyu/stage/reda/' || '" + str(target) +
                "' || '/' || '" + str(target) +
                "' || sa.container || ' && ' || E'cp \"/nyu/store/' || substr(cast(sha1 as varchar(80)), 3, 2) || '/' || right(cast(sha1 as varchar(80)), -4) || ' /nyu/stage/reda/' || '"
                + str(target) + "' || '/' || '" + str(target) +
                "' || container || '/' || CASE WHEN a.name LIKE '%.___' IS FALSE THEN a.name || '.' || f.extension[1] || E'\"'  ELSE a.name END from slot_asset sa inner join asset a on sa.asset = a.id inner join format f on a.format = f.id where a.volume = "
                + str(source) + ") TO '/tmp/volume_" + str(target) + ".sh';")


if __name__ == '__main__':
    if args.file is None:
        autoPrepCSV(args.__source_volume_id, args.__target_volume_id)
    else:
        parseCSV(args.file, args.source, args.target)
