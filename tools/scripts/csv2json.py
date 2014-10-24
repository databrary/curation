import csv
import os
import sys
from pprint import pprint
import json
import fields

'''TODO: 
        Make output validate specifically against ../../spec/volume.json
        Reflect multirecords for participants in containers
        Less hardcoded headers or reflect a standard based on JSON schema
        Probably just want to move to python 3 if nothing holding back in 2.7
''' 


try:
    _session_csv = sys.argv[1]
    _participant_csv = sys.argv[2]
except:
    print 'To run this, please add paths to two csv files as arguments: e.g. `python csv2json.py session.csv participants.csv`'
    sys.exit()


def getParticipantMap(p_csvFile):
    participantMap = {};
    f = open(p_csvFile, 'rb')
    p_reader = csv.reader(f)
    p_headers = p_reader.next()


    for rec in p_reader:
        vals = {}
        for z in range(len(p_headers)):
            vals[p_headers[z]] = rec[z]

        participantMap[rec[0]] = vals

    return participantMap              


def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rb') as s_input: 
        s_reader = csv.reader(s_input)
        s_headers = s_reader.next()

        data = []
        
        p_map = getParticipantMap(p_csvFile)
        
        for row in s_reader:
            records = {}
            record = {}
            record['records'] = {}
            record['records']['participants'] = []
            
            for i in range(len(s_headers)):

                header = s_headers[i].strip()


                if header == "participantID":
                    record['records']['participants'].append(p_map[row[3]])

                elif header == "tasks":
                    record['records'][s_headers[i]] = []
                    task_list = row[i].split(';')

                    for j in range(len(task_list)):

                        record['records'][s_headers[i]].append(task_list[j].strip())

                elif header in fields.available_fields:
                    record['records'][s_headers[i]] = row[i] 


                else:
                    record[s_headers[i]] = row[i]
                
                
            data.append(record)

    res = json.dumps(data, indent=4)

        
    j = open('../o/output.json', 'w')
    j.write(res)

if __name__ == "__main__":
    parseCSV2JSON(_session_csv, _participant_csv)




