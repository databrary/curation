import csv
import os
import sys
sys.path.append('./utils')
from pprint import pprint
import json
import fields

'''TODO:
        Make output validate specifically against ../../spec/volume.json
         - ensure type casts for ingest
        Less hardcoded headers or reflect a standard based on JSON schema
        Probably just want to move to python 3 if nothing holding back in 2.7
'''


try:
    _session_csv = sys.argv[1]     #session metadata (csv format)
    _participant_csv = sys.argv[2] #participant metadata (csv format)
    _filepath_prefix = sys.argv[3] #filename on server where assets are kept
except:
    print '''To run this, please add paths to two csv files and a name
             for the file where the video data is kept as arguments:
             e.g. `python csv2json.py session.csv participants.csv study1_files`'''
    sys.exit()


def giveMeCSV(file):
    f = open(file, 'rb')
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
    p_headers = p_reader.next()


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
    rhead = r.next()

    sessionMap = makeOuterMostElements(r)

    vol = giveMeCSV(s_csvFile)
    vheaders = vol.next()

    for i in vol:
        
        participantID = i[2]
        
        sessionMap[i[0]]['records'].append({'pID': participantID})
        
    '''the following then deduplicates participants in any given containers participant record'''  
    for k, v in sessionMap.iteritems():
        deduped = {d['pID']:d for d in sessionMap[k]['records']}.values()
        sessionMap[k]['records'] = deduped


    return sessionMap

def makeOuterMostElements(csvReader):
    '''make an empty dictionary with the session id for keys'''
    emptydict = {}

    for n in csvReader:
        emptydict[n[0]] = {'assets':[], 'records':[]}


    return emptydict



def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rb') as s_input:
        s_reader = csv.reader(s_input)
        s_headers = s_reader.next()

        p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)

        for row in s_reader:
            name=row[0]
            s_curr = s_map[name]
            date=row[1]

            path = row[10]
            clipArr = [row[7], row[8]] if row[7] != '' else ['auto']
            segment = [row[9]] if row[9] != '' else ['auto'] #row[10] is a placeholder for now
            classification = row[6].upper() if row[6] != '' else 'RESTRICTED'
            top = True if row[3] != '' else False
            pilot = row[4]
            exclusion = row[5]
            condition = row[13]
            group = row[14]
            setting = row[16]
            state = row[17]
            country = row[18]


            for i in range(len(s_headers)):
                header = cleanVal(s_headers[i])

                '''not in schema, need to pull in?'''
                #if header == "tasks":
                #    task_list = row[i].split(';')

                #    for j in range(len(task_list)):
                #        if cleanVal(task_list[j]) not in s_map[row[0]]['records']['tasks']:
                #            s_map[row[0]]['records']['tasks'].append(cleanVal(task_list[j]))

                

                if header == "participantID":
                    for i in range(len(s_curr['records'])):
                        target = s_curr['records'][i]
                        '''missing: date and age, in days.'''
                        if 'pID' in target:
                            target['category'] = p_map[target['pID']]['category']
                            target['birthdate'] = p_map[target['pID']]['birthdate']
                            target['ethnicity'] = p_map[target['pID']]['ethnicity']
                            target['race'] = p_map[target['pID']]['race']
                            target['language'] = p_map[target['pID']]['language']
                            target['disability'] = p_map[target['pID']]['disability']
                            target['gender'] = p_map[target['pID']]['gender']


                elif 'file_' in header:
                    s_curr['assets'].append({'file': row[i], 
                                             'clip': clipArr, 
                                             'segment': segment, 
                                             'classification': classification
                                             })
                
                elif header == 'pilot':
                    s_curr['records'].append({'category': 'pilot',
                                              'ident': pilot})

                elif header == 'exlcusion':
                    s_curr['records'].append({'category': 'exclusion',
                                              'reason': exclusion})

                elif header == 'condition':
                    s_curr['records'].append({'category': 'condition',
                                              'ident': condition})

                elif header == 'setting':
                    s_curr['records'].append({'category': 'context',
                                              'setting': setting,
                                              'state': state,
                                              'country': country})

                elif header == 'name':

                    s_curr[s_headers[i]] = name

                elif header == 'date':

                    s_curr[s_headers[i]] = date


                elif header == 'top':

                    s_curr[s_headers[i]] = top

                
        

        data = {

            "name": _filepath_prefix,
            "containers": s_map.values()
        }



    res = json.dumps(data, indent=4)

    output_dest = '../o/' + _filepath_prefix + "_output.json"
    j = open(output_dest, 'w')
    j.write(res)

if __name__ == "__main__":
    parseCSV2JSON(_session_csv, _participant_csv)
