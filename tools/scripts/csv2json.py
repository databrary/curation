import csv
import os
import re
import sys
import json
import collections
from pprint import pprint
from utils import csv_helpers as ch
from datetime import datetime
import argparse

################### COMMAND LINE ARGUMENT HANDLING #####################################

parser = argparse.ArgumentParser(description='Command line tool used internally to prepare CSVs full of metadata into JSON Databrary ingest packages')
parser.add_argument('-s', '--sessionfile', help='Path to session metadata file. Is required', required=True)
parser.add_argument('-p', '--participantfile', help='Path to participant metadata file. Is optional', required=False)
parser.add_argument('-f', '--fileprefix', help='Prefix to be used in naming the output file', required=True)
parser.add_argument('-n', '--volumename', help='Provide the full name for the volume, ingest requires this for validation', required=True)
args = vars(parser.parse_args())

_session_csv = args['sessionfile']     #session metadata (csv format)
_participant_csv = args['participantfile'] #participant metadata (csv format)
_filepath_prefix = args['fileprefix'] #prefix to add to the output file, preferable something reflecting the dataset
_volume_name = args['volumename']
################## DATA STRUCTURE PREP AND MANIPULATION #########################

_participantMetrics = {
    ''' dict for all participant metadata. 
        key is string literal for the property, 
        value is whether it needs to be capitalized or not (so it validates).
    '''
    "language": False,
    "ethnicity": False,
    "birthdate": False,
    "gender": True,
    "race": False,
    "disability": False,
    "description": False,
    "info": False, 
    "gestational age": False,
    "pregnancy term": True
}

def assignParticipantMd(t, p, k, v):
    '''
    t = the current list of all participant record being updated
    p = the current participant being update
    k = the string literal for the particpant metadata field
    v = the boolean value of whether it should be title cased or not 
    '''

    if k in p and p[k] != '':
        if k == "birthdate":
            t[k] = ensureDateFormat(p[k].strip())
        elif v == True:
            t[k] = p[k].capitalize().strip()
        else:
            t[k] = p[k].strip()


def getParticipantMap(p_csvFile):
    '''This will give us back a dictionary with participant IDs as keys and
        their records in the form of dictionaries as the values'''
    participantMap = {};
    p_reader = ch.giveMeCSV(p_csvFile)
    p_headers = next(p_reader)
    p_idx = ch.getHeaderIndex(p_headers)

    for rec in p_reader:
        
        vals = {p_headers[z]: rec[z] for z in range(len(p_headers))}

        participantMap[rec[p_idx['participantID']]] = vals

    return participantMap

def getSessionMap(s_csvFile):
    '''This will give us back a dictionary where the unique session names (IDs) are associated with a dictionary of
       values containing participant'''

    r = ch.giveMeCSV(s_csvFile)
    rhead = next(r)

    sessionMap = makeOuterMostElements(r)

    vol = ch.giveMeCSV(s_csvFile)
    vheaders = next(vol)
    vHIdx = ch.getHeaderIndex(vheaders)

    for i in vol:
        if 'participantID' in vHIdx:

            participantID = i[vHIdx['participantID']]
            sessionMap[i[0]]['records'].append({'ID': participantID, 'key': participantID, 'category': 'participant'})

    '''the following then deduplicates participants in any given containers participant record'''
    for k, v in sessionMap.items():
        deduped = list({d['ID']:d for d in sessionMap[k]['records']}.values())
        sessionMap[k]['records'] = deduped


    return sessionMap

def makeOuterMostElements(csvReader):
    '''make an empty dictionary with the session id for keys'''
    emptydict = {}

    for n in csvReader:
        emptydict[n[0]] = {'assets':[], 'records':[]}


    return emptydict

def makeRecordsFromList(category, list_things, positions):
    recObjs = []
    
    position_formatted = []

    if positions is not None:
        for i in positions:
            clip = i.split('-')
            if clip[0] != '#':
                if clip[1] == '$':
                    position_formatted.append([clip[0], None])
                else:
                    position_formatted.append([clip[0], clip[1]])


    for i in range(len(list_things)):

        if category == 'task':
        
            task = list_things[i].strip()
            if "|" in task:
                task_txt = task.split("|")[0]
                task_id = int(task.split("|")[1])
                taskObj = {'category':category, 
                           'name':task_txt, 
                           'key':task_txt,
                           'id': task_id}

            else:    
                taskObj = {'category':category, 
                           'name':task, 
                           'key':task}

            if position_formatted != []:
                    taskObj['position'] = position_formatted[i]

            if not any(taskObj == d for d in recObjs):
                recObjs.append(taskObj)

        if category == 'exclusion':

            excl = list_things[i].strip()
            if excl != '#':
                exclObj = {'category':category, 
                           'reason':excl, 
                           'key':excl}
                if positions is not None:
                    exclObj['position'] = position_formatted[i]
                recObjs.append(exclObj)

        if category == 'condition':

            cond = list_things[i].strip()
            condObj = {'category':category, 
                       'name':cond, 
                       'key':cond}
            recObjs.append(condObj)


    return recObjs

def recordAppend(obj, val, cat):

    if cat == 'pilot':
        obj['records'].append({'category': cat,
                               'key': val
                           })

    else: 
        obj['records'].append({'category': cat,
                               'name': val,
                               'key': val
                               })

def checkClipsStatus(file_path, file_name, file_position, file_classification, *args):


    '''Here determine how to handle the creation of assets:
        pos_start, pos_end, neg_start, neg_end'''

    pos, neg = args #one or more clips or None
    
    entries = []
    
    if pos == None and neg == None:
        clipArr = ""
    else:
        clipArr = []

    if pos != None:

        if pos != "":
            clip_ins = pos.split(';')
            num_of_clip_ins = len(clip_ins)

            for i in clip_ins:
                times = i.split('-')
                clipArr.append((times[0].strip(), times[1].strip()))


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
                            'name': file_name, 
                            'position': i[0] if file_position is 'auto' or file_position == "" else file_position, 
                            'clip': [i[0], i[1]], 
                            'release': file_classification, 
                            'options': ""})

    else:
        if file_position is not None: 
            file_position = None if file_position == 'null' else file_position
            entries.append({'file': file_path,
                            'name': file_name, 
                            'position': file_position, 
                            'release': file_classification, 
                            'options': ""})
        else:
            entries.append({'file': file_path,
                            'name': file_name, 
                            'position': "", 
                            'release': file_classification, 
                            'options': ""})

    return entries


def ensureDateFormat(date):
    if '/' in date:
        date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    return date

def key_checker(item):
    '''function for checking if a string contains both alpha and numeric characters
    like V199'''
    ikey = item['key']
    key_pattern = re.compile( r"^(\D+)[\-\_]?(\d+)$")
    if type(ikey) is str: 
        if ikey.isalnum() is False:
            return ikey
        elif ikey.isdigit():
            return int(ikey)
        elif key_pattern.match(ikey):
            m = key_pattern.match(ikey)
            return m.group(1), int(m.group(2))
        else:
            print("seems you have a key that we haven't accounted for, go look at your keys.")
            sys.exit()
    else:
        return ikey
############################### MAIN ####################################

def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rt') as s_input:
        s_reader = csv.reader(s_input)
        s_headers = next(s_reader)

        headerIndex = ch.getHeaderIndex(s_headers)

        if p_csvFile != "None":
            p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)

        for row in s_reader:

            name = row[headerIndex['name']] if 'name' in headerIndex else None
            key = row[headerIndex['key']] if 'key' in headerIndex else name
            dbrary_session_id = int(row[headerIndex['slot_id']]) if 'slot_id' in headerIndex else None 
            s_curr = s_map[key]

            date = ch.assignIfThere('date', headerIndex, row, None)

            path = ch.assignIfThere('filepath', headerIndex, row, None)
            t_positions = ch.assignIfThere('task_positions', headerIndex, row, None)
            task_positions = t_positions.split(';') if t_positions is not None else t_positions
            ex_positions = ch.assignIfThere('excl_positions', headerIndex, row, None)
            excl_positions = ex_positions.split(';') if ex_positions is not None else ex_positions
            top = True if 'top' in headerIndex and row[headerIndex['top']] != '' else False
            pilot = ch.assignIfThere('pilot', headerIndex, row, None)
            exclusion = makeRecordsFromList('exclusion', row[headerIndex['exclusion']].split(';'), excl_positions) if 'exclusion' in headerIndex and row[headerIndex['exclusion']] != '' else ''
            condition = makeRecordsFromList('condition', row[headerIndex['condition']].split(';'), None) if 'condition' in headerIndex and row[headerIndex['condition']] != '' else ''
            group = ch.assignIfThere('group', headerIndex, row, None)
            setting = ch.assignIfThere('setting', headerIndex, row, None)
            state = ch.assignIfThere('state', headerIndex, row, None)
            country = ch.assignIfThere('country', headerIndex, row, None)
            consent = ch.assignIfThere('consent', headerIndex, row, None)
            language = ch.assignIfThere('language', headerIndex, row, None)
            t_options = row[headerIndex['transcode_options']].split(' ') if 'transcode_options' in headerIndex and row[headerIndex['transcode_options']] != '' else ''
            tasks = makeRecordsFromList('task', row[headerIndex['tasks']].split(';'), task_positions) if 'tasks' in headerIndex and row[headerIndex['tasks']] != '' else ''

            context = {}
            context['category'] = 'context'
            context['key'] = 'context'
            if setting != None:
                context['setting'] = setting.title()
            if state != None:
                context['state'] = state
            if country != None:
                context['country'] = country


            for i in range(len(s_headers)):
                header = ch.cleanVal(s_headers[i])


                if header == 'participantID':
                    for i in range(len(s_curr['records'])):
                        target = list(s_curr['records'])[i]
                        '''missing: date and age, in days.'''
                        if 'category' in target and target['category'] == 'participant' and target['ID'] != '':

                            p_target = p_map[target['ID']]

                            for _k, _v in _participantMetrics.items():
                                assignParticipantMd(target, p_target, _k, _v)

                elif 'file_' in header and row[i] != '':
                    path = path if path.endswith("/") else path + "/"
                    fpath = path+row[i]
                    ##### CLIP STUFF #####
                    asset_no = header.split("_")[1]
                    pos_clip = "clip_in_" 
                    neg_clip = "clip_out_" 
                    file_name = "fname_" + asset_no
                    file_position = "fposition_" + asset_no
                    file_classification = "fclassification_" + asset_no
                    fname = ch.assignIfThere(file_name, headerIndex, row, None)
                    fposition = ch.assignWithEmpty(file_position, headerIndex, row, 'auto')
                    fclassification = ch.assignWithEmpty(file_classification, headerIndex, row, None)
                    prefixes = (pos_clip, neg_clip)
                    clip_options = tuple(ch.assignWithEmpty(j+asset_no, headerIndex, row, None) for j in prefixes)
                    asset_entry = checkClipsStatus(fpath, fname, fposition, fclassification, *clip_options) #sends either 1 or more sets of clips or none

                    for z in asset_entry:
                        if fclassification is not None:
                            z['release'] = fclassification.upper()
                        else:
                            z['release'] = None
                        if t_options != '':
                            z['options'] = t_options
                        else:
                            del z['options']
                        z['position'] = fposition if z['position'] == '' else z['position']
                        if z['name'] is None:
                            del z['name']
                        if z not in s_curr['assets']:
                            s_curr['assets'].append(z)

                    ##### CLIP STUFF #####

                elif header == 'pilot' and pilot != None:
                    recordAppend(s_curr, pilot, 'pilot')
                    
                elif header == 'exclusion' and exclusion != '':
                    for excl in exclusion:
                        s_curr['records'].append(excl)
                    
                elif header == 'condition' and condition != '':
                    for c in condition:
                        s_curr['records'].append(c)

                elif header == 'group' and group != None:
                    recordAppend(s_curr, group, 'group')

                elif header == 'setting' and len(context) > 2 and not any(context == d for d in s_curr['records']):
                    s_curr['records'].append(context)

                elif header == 'tasks' and tasks != '':
                    for task in tasks:
                        if not any(task == f for f in s_curr['records']):
                            s_curr['records'].append(task)

                if date is not None:
                    s_curr['date'] = ensureDateFormat(date)
                
                if consent is not None:
                    s_curr['release'] = consent.upper()

                if dbrary_session_id is not None:
                    s_curr['id'] = dbrary_session_id

                s_curr['top'] = top
                s_curr['name'] = name 
                s_curr['key'] = key
                

                if s_curr['name'] is None:
                    del s_curr['name']


        data = {

            'name': _volume_name,
            'containers': sorted(list(s_map.values()), key=key_checker)
        }


    res = json.dumps(data, indent=4)

    output_dest = '../o/' + _filepath_prefix + '_output.json'
    j = open(output_dest, 'wt')
    j.write(res)

if __name__ == '__main__':
    parseCSV2JSON(_session_csv, _participant_csv)
