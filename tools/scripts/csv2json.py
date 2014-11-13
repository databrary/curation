import csv
import os
import sys
from pprint import pprint
import json



try:
    _session_csv = sys.argv[1]     #session metadata (csv format)
    _participant_csv = sys.argv[2] #participant metadata (csv format)
    _filepath_prefix = sys.argv[3] #filename on server where assets are kept
except:
    print('''To run this, please add paths to two csv files and a name
             for the file where the video data is kept as arguments:
             e.g. `python csv2json.py session.csv participants.csv study1_files`''')
    sys.exit()


def giveMeCSV(file):
    f = open(file, 'rt')
    r = csv.reader(f)
    return r

def cleanVal(i):
    i = i.strip()
    return i

def getHeaderIndex(headerlist):
    headerIndex = {}
    for i in range(len(headerlist)):
        headerIndex[headerlist[i]] = i

    return headerIndex


def getParticipantMap(p_csvFile):
    '''This will give us back a dictionary with participant IDs as keys and
        their records in the form of dictionaries as the values'''
    participantMap = {};
    p_reader = giveMeCSV(p_csvFile)
    p_headers = next(p_reader)


    for rec in p_reader:
        vals = {}
        for z in range(len(p_headers)):
            vals[p_headers[z]] = rec[z]

        participantMap[rec[0]] = vals

    return participantMap

def getSessionMap(s_csvFile):
    '''This will give us back a dictionary where the unique session names (IDs) are associated with a dictionary of
       values containing participant'''

    r = giveMeCSV(s_csvFile)
    rhead = next(r)

    sessionMap = makeOuterMostElements(r)

    vol = giveMeCSV(s_csvFile)
    vheaders = next(vol)
    vHIdx = getHeaderIndex(vheaders)

    for i in vol:

        participantID = i[vHIdx['participantID']]

        sessionMap[i[0]]["records"].append({"ident": participantID, "key": participantID})

    '''the following then deduplicates participants in any given containers participant record'''
    for k, v in sessionMap.items():
        deduped = list({d["ident"]:d for d in sessionMap[k]["records"]}.values())
        sessionMap[k]["records"] = deduped


    return sessionMap

def makeOuterMostElements(csvReader):
    '''make an empty dictionary with the session id for keys'''
    emptydict = {}

    for n in csvReader:
        emptydict[n[0]] = {"assets":[], "records":[]}


    return emptydict



def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rt') as s_input:
        s_reader = csv.reader(s_input)
        s_headers = next(s_reader)

        headerIndex = getHeaderIndex(s_headers)

        p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)

        for row in s_reader:

            name=row[headerIndex['name']]
            s_curr = s_map[name]

            date = row[headerIndex['date']] #default to not real date, but should be a date

            path = row[headerIndex['filepath']]
            clipArr = [row[headerIndex['clip_in']], row[headerIndex['clip_out']]] if row[headerIndex['clip_in']] != "" else ""
            position = [row[headerIndex['position']]] if row[headerIndex['position']] != "" else ["0:00"]
            classification = row[headerIndex['classification']].upper() if row[headerIndex['classification']] != "" else "RESTRICTED"
            top = True if row[headerIndex['top']] != "" else False
            pilot = row[headerIndex['pilot']]
            exclusion = row[headerIndex['exclusion']]
            condition = row[headerIndex['condition']]
            group = row[headerIndex['group']]
            setting = row[headerIndex['setting']]
            state = row[headerIndex['state']]
            country = row[headerIndex['country']]
            consent = row[headerIndex['consent']] if row[headerIndex['consent']] != "" else None
            language = row[headerIndex['language']] 

            context = {}
            context['category'] = 'context'
            context['key'] = 'context'
            if setting != '':
                context['setting'] = setting
            if state != '':
                context['state'] = state
            if country != '':
                context['country'] = country



            for i in range(len(s_headers)):
                header = cleanVal(s_headers[i])

                '''not in schema, need to pull in?'''
                #if header == "tasks":
                #    task_list = row[i].split(';')

                #    for j in range(len(task_list)):
                #        if cleanVal(task_list[j]) not in s_map[row[0]]['records']['tasks']:
                #            s_map[row[0]]['records']['tasks'].append(cleanVal(task_list[j]))



                if header == 'participantID':
                    for i in range(len(s_curr["records"])):
                        target = list(s_curr["records"])[i]
                        '''missing: date and age, in days.'''
                        if 'ident' in target:

                            p_target = p_map[target["ident"]]


                            if p_target["category"] != '':
                                target["category"] = p_target["category"]
                            if p_map[target['ident']]["birthdate"] != '':
                                target["birthdate"] = p_target["birthdate"]
                            if p_target["ethnicity"] != '':
                                target["ethnicity"] = p_target["ethnicity"]
                            if p_target["race"] != '':
                                target["race"] = p_target["race"]
                            if p_target["language"] != '':
                                target["language"] = p_target["language"]
                            if p_target["disability"] != '':
                                target["disability"] = p_target["disability"]
                            if p_target["gender"] != '':
                                target["gender"] = p_target["gender"].title()


                elif 'file_' in header:

                    asset_entry = {"file": path+row[i], "position": position, "clip": clipArr, "classification": classification}

                    if clipArr == "":
                        del asset_entry['clip']


                    s_curr["assets"].append(asset_entry)



                elif header == 'pilot' and pilot != '':
                    s_curr["records"].append({"category": "pilot",
                                              "ident": pilot,
                                              "key": pilot})

                elif header == 'exlcusion' and exclusion != '':
                    s_curr["records"].append({"category": "exclusion",
                                              "reason": exclusion,
                                              "key": exclusion})

                elif header == 'condition' and condition != '':
                    s_curr["records"].append({"category": "condition",
                                              "ident": condition,
                                              "key": condition})

                elif len(context) > 2:
                    s_curr["records"].append(context)


                s_curr['date'] = date
                s_curr['top'] = top
                s_curr['name'] = s_curr['key'] = name
                s_curr["consent"] = consent






        data = {

            "name": _filepath_prefix,
            "containers": list(s_map.values())
        }

    res = json.dumps(data, indent=4)

    output_dest = '../o/' + _filepath_prefix + "_output.json"
    j = open(output_dest, 'wt')
    j.write(res)

if __name__ == "__main__":
    parseCSV2JSON(_session_csv, _participant_csv)
