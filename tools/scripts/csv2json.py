import csv
import os
import sys
import json
import collections


################### COMMAND LINE ARGUMENT HANDLING #####################################
try:
    _session_csv = sys.argv[1]     #session metadata (csv format)
    _participant_csv = sys.argv[2] #participant metadata (csv format)
    _filepath_prefix = sys.argv[3] #filename on server where assets are kept
except:
    print('''To run this, please add paths to two csv files and a name
             for the file where the video data is kept as arguments:
             e.g. `python csv2json.py session.csv participants.csv study1_files`''')
    sys.exit()


################### QUICK OPERATIONS FOR REDUNDANT TASKS ###############################
def giveMeCSV(file):
    f = open(file, 'rt') 
    return csv.reader(f)

def cleanVal(i):
    return i.strip()

def getHeaderIndex(headerlist):
    return {headerlist[i]: i for i in range(len(headerlist))}

def assignIfThere(k, index, row, assignthis):
    '''all purpose check for key in header index so we know to assign a value for the row or not
        so we do not need empty columns in the spreadsheet'''

    return row[index[k]] if k in index and row[index[k]] != '' else assignthis

def assignWithEmpty(k, index, row, assignthis):
    '''assign none if does not exist, or assign with empty string if the column does exist'''

    return row[index[k]] if k in index else assignthis



################## DATA STRUCTURE PREP AND MANIPULATION #########################
def getParticipantMap(p_csvFile):
    '''This will give us back a dictionary with participant IDs as keys and
        their records in the form of dictionaries as the values'''
    participantMap = {};
    p_reader = giveMeCSV(p_csvFile)
    p_headers = next(p_reader)


    for rec in p_reader:
        
        vals = {p_headers[z]: rec[z] for z in range(len(p_headers))}

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

        sessionMap[i[0]]['records'].append({'ident': participantID, 'key': participantID, 'category': 'participant'})

    '''the following then deduplicates participants in any given containers participant record'''
    for k, v in sessionMap.items():
        deduped = list({d['ident']:d for d in sessionMap[k]['records']}.values())
        sessionMap[k]['records'] = deduped


    return sessionMap

def makeOuterMostElements(csvReader):
    '''make an empty dictionary with the session id for keys'''
    emptydict = {}

    for n in csvReader:
        emptydict[n[0]] = {'assets':[], 'records':[]}


    return emptydict

def makeTasks(tasklist):
    taskObjs = []


    for i in range(len(tasklist)):
        taskObj = {'category':'task', 'ident':tasklist[i], 'key':tasklist[i]}
        if not any(taskObj == d for d in taskObjs):
            taskObjs.append(taskObj)

    return taskObjs

def recordAppend(obj, val, cat):

    if cat == 'exclusion':
        obj['records'].append({'category': cat,
                               'reason': val,
                               'key': val
                           })
    elif cat == 'pilot':
        obj['records'].append({'category': cat,
                               'key': val
                           })

    else: 
        obj['records'].append({'category': cat,
                               'ident': val,
                               'key': val
                               })

def checkClipsStatus(file_path, *args):


    '''Here determine how to handle the creation of assets:
        pos_start, pos_end, neg_start, neg_end'''

    pos = args[0] #one or more clips or None
    neg = args[1] # '' ''  ''    ''  ''  ''

    entries = []
    clipArr = []

    if pos != None:

        if pos != "":
            clip_ins = pos.split(';').strip()
            num_of_clip_ins = len(clip_ins)

            for i in clip_ins:
                times = i.split('-').strip()
                clipArr.append((times[0], times[1]))


        else: 
            clipArr = ""
    

    if neg != None:

        if neg != "":
            clip_outs = neg.split(';')
            num_of_clip_outs = len(clip_outs)

            if num_of_clip_outs == 1:
                times = clip_outs[0].split('-')
                time_in = times[0].strip()
                time_out = times[1].strip()

                if time_in == '0:00':
                    clipArr.append((time_out, None))
                elif time_out == "$":
                    clipArr.append(("0:00", time_in))
                else:
                    clipArr.append(("0:00", time_in))
                    clipArr.append((time_out, None))

            if num_of_clip_outs > 1:

                first_times = clip_outs[0].split('-')
                last_times = clip_outs[-1].split('-')
                mid_times = clip_outs[1:-1]

                first_in = first_times[0].strip()
                first_out = first_times[1].strip()
                last_in = last_times[0].strip()
                last_out = last_times[1].strip()

                if first_in != '0:00':
                    clipArr.append(("0:00", first_in))


                if len(mid_times) == 0:

                    if first_in == '0:00':
                        clipArr.append((first_out, last_in))
                
                if len(mid_times) > 0:
                    recent = first_out
                    for z in mid_times:
                        curr_clip = z.split('-')
                        curr_in = curr_clip[0].strip()
                        curr_out = curr_clip[1].strip()
                        clipArr.append((recent, curr_in))
                        recent = curr_out
                    clipArr.append((curr_out, last_in))

                if last_out != '$':
                        clipArr.append((last_out, None))


        else:
            clipArr = ""



    if clipArr is not "":
        for i in clipArr:
            entries.append({'file': file_path, 
                                'position': "", 
                                'clip': [i[0], i[1]], 
                                'classification': "", 
                                'options': ""})

    else: 
        entries.append({'file': file_path, 
                                'position': "", 
                                'classification': "", 
                                'options': ""})


    return entries

############################### MAIN ####################################

def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rt') as s_input:
        s_reader = csv.reader(s_input)
        s_headers = next(s_reader)

        headerIndex = getHeaderIndex(s_headers)

        p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)

        for row in s_reader:

            name = row[headerIndex['name']] if 'name' in headerIndex else None
            key = row[headerIndex['key']] if 'key' in headerIndex else name 
            s_curr = s_map[key]

            date = row[headerIndex['date']]

            path = row[headerIndex['filepath']]
            position = assignIfThere('position', headerIndex, row, 'auto')
            classification = assignIfThere('classification', headerIndex, row, 'RESTRICTED').upper()
            top = True if 'top' in headerIndex and row[headerIndex['top']] != '' else False
            pilot = row[headerIndex['pilot']]
            exclusion = row[headerIndex['exclusion']]
            condition = row[headerIndex['condition']]
            group = row[headerIndex['group']]
            setting = row[headerIndex['setting']]
            state = row[headerIndex['state']]
            country = row[headerIndex['country']]
            consent = assignIfThere('consent', headerIndex, row, None)
            language = row[headerIndex['language']]
            t_options = row[headerIndex['transcode_options']].split(' ') if 'transcode_options' in headerIndex and row[headerIndex['transcode_options']] != '' else ''
            tasks = makeTasks(row[headerIndex['tasks']].split(';')) if 'tasks' in headerIndex and row[headerIndex['tasks']] != '' else ''


            context = {}
            context['category'] = 'context'
            context['key'] = 'context'
            if setting != '':
                context['setting'] = setting.title()
            if state != '':
                context['state'] = state
            if country != '':
                context['country'] = country


            for i in range(len(s_headers)):
                header = cleanVal(s_headers[i])


                if header == 'participantID':
                    for i in range(len(s_curr['records'])):
                        target = list(s_curr['records'])[i]
                        '''missing: date and age, in days.'''
                        if 'category' in target and target['category'] == 'participant':

                            p_target = p_map[target['ident']]


                            if p_map[target['ident']]['birthdate'] != '':
                                target['birthdate'] = p_target['birthdate']
                            if 'ethnicity' in p_target and p_target['ethnicity'] != '':
                                target['ethnicity'] = p_target['ethnicity']
                            if 'race' in p_target and p_target['race'] != '':
                                target['race'] = p_target['race']
                            if 'langauge' in p_target and p_target['language'] != '':
                                target['language'] = p_target['language']
                            if 'disability' in p_target and p_target['disability'] != '':
                                target['disability'] = p_target['disability']
                            if 'gender' in p_target and p_target['gender'] != '':
                                target['gender'] = p_target['gender'].title()




                elif 'file_' in header and row[i] != '':

                    fpath = path+row[i]

                    ##### CLIP STUFF #####
                    asset_no = header.split("_")[1]

                    pos_clip = "clip_in_" 
                    neg_clip = "clip_out_" 
                    
                    prefixes = (pos_clip, neg_clip)

                    clip_options = tuple(assignWithEmpty(i+asset_no, headerIndex, row, None) for i in prefixes)
                    
                    asset_entry = checkClipsStatus(fpath,*clip_options) #sends either 1 or more sets of clips or none


                    for i in asset_entry:
                        i['classification'] = classification
                        i['options'] = t_options
                        i['position'] = position
                        if t_options == '':
                            del i['options']

                    for j in asset_entry:
                        if j not in s_curr['assets']:
                            s_curr['assets'].append(j)

                    ##### CLIP STUFF #####


                elif header == 'pilot' and pilot != '':
                    recordAppend(s_curr, pilot, 'pilot')
                    

                elif header == 'exclusion' and exclusion != '':
                    recordAppend(s_curr, exclusion, 'exclusion')
                    

                elif header == 'condition' and condition != '':
                    recordAppend(s_curr, condition, 'condition')

                elif header == 'group' and group != '':
                    recordAppend(s_curr, group, 'group')


                elif header == 'setting' and len(context) > 2 and not any(context == d for d in s_curr['records']):
                    s_curr['records'].append(context)

                elif header == 'tasks' and tasks != '':
                    for task in tasks:
                        if not any(task == f for f in s_curr['records']):
                            s_curr['records'].append(task)



                s_curr['date'] = date
                s_curr['top'] = top
                s_curr['name'] = name 
                s_curr['key'] = key
                s_curr['consent'] = consent.upper() if consent is not None else consent

                if s_curr['name'] is None:
                    del s_curr['name']


        data = {

            'name': _filepath_prefix,
            'containers': sorted(list(s_map.values()), key=lambda k: int(k['key']) if type(k['key']) is str and k['key'].isdigit() else k['key'] )
        }


    res = json.dumps(data, indent=4)

    output_dest = '../o/' + _filepath_prefix + '_output.json'
    j = open(output_dest, 'wt')
    j.write(res)

if __name__ == '__main__':
    parseCSV2JSON(_session_csv, _participant_csv)
