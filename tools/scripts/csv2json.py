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

    for i in vol:

        participantID = i[2]

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
        emptydict[n[0]] = {"assets":[], "records":[], "consent":[]}


    return emptydict



def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rt') as s_input:
        s_reader = csv.reader(s_input)
        s_headers = next(s_reader)

        p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)

        for row in s_reader:

            name=row[0]
            s_curr = s_map[name]
            date = row[1] #default to not real date, but should be a date

            path = row[18]
            clipArr = [row[15], row[16]] if row[15] != "" else ""
            position = [row[17]] if row[17] != "" else ["0:00"]
            classification = row[6].upper() if row[6] != "" else "RESTRICTED"
            top = True if row[3] != "" else False
            pilot = row[4]
            exclusion = row[5]
            condition = row[12]
            group = row[13]
            setting = row[7]
            state = row[9]
            country = row[8]
            consent = row[11] if row[11] != "" else "PRIVATE"
            language = row[10]

            context = []
            if setting != '':
                context.append(setting)
            if state != '':
                context.append(state)
            if country != '':
                context.append(country)



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

                elif header == 'setting' and len(context) > 0:
                    s_curr["records"].append({"category": "context",
                                              "key": "context",
                                              "setting": setting,
                                              "state": state,
                                              "country": country
                                              })

                elif header == "consent":
                    s_curr["consent"].append({"consent":consent})

                elif header == 'name':

                    s_curr[s_headers[i]] = s_curr['key'] = name

                elif header == 'date' and date != '':

                    s_curr[s_headers[i]] = date


                elif header == 'top' and top != '':

                    s_curr[s_headers[i]] = top




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
