import csv
import os
import sys
from pprint import pprint
import json


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

    

available_fields = ["SETTING", "COUNTRY", "STATE"]



def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rb') as s_input: 
        s_reader = csv.reader(s_input)
        s_headers = s_reader.next()

        data = []
        
        p_map = getParticipantMap(p_csvFile)
        
        for row in s_reader:
            records = {}
            record = {}
            record['RECORDS'] = {}
            record['RECORDS']['PARTICIPANTS'] = []
            
            for i in range(len(s_headers)):

                header = s_headers[i].strip()


                if header == "SUBID":
                    record['RECORDS']['PARTICIPANTS'].append(p_map[row[3]])

                elif header == "TASK":
                    record['RECORDS'][s_headers[i]] = []
                    task_list = row[i].split(';')

                    for j in range(len(task_list)):

                        record['RECORDS'][s_headers[i]].append(task_list[j].strip())

                elif header in available_fields:
                    record['RECORDS'][s_headers[i]] = row[i] 


                else:
                    record[s_headers[i]] = row[i]
                
                
            data.append(record)

    res = json.dumps(data, indent=4)

        
    j = open('output.json', 'w')
    j.write(res)

if __name__ == "__main__":
    parseCSV2JSON(_session_csv, _participant_csv)




