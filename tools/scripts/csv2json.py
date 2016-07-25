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
parser.add_argument('-a', '--assisted', help='This will tell the script that you are preparing data for assisted curation, so pointing at a file by asset id, and not file path in stage', required=False, action="store_true")
args = vars(parser.parse_args())

_session_csv = args['sessionfile']     #session metadata (csv format)
_participant_csv = args['participantfile'] #participant metadata (csv format)
_filepath_prefix = args['fileprefix'] #prefix to add to the output file, preferable something reflecting the dataset
_volume_name = args['volumename']
_assisted_curation = args['assisted']

################## DATA STRUCTURE PREP AND MANIPULATION #########################

    #array for context metadata, largely just to avoid repeition when assigning these fields in code below

_contextMetrics = ["setting", "state", "country", "language"]

    #dict for all participant metadata. 
    #key is string literal for the property, 
    #value is whether it needs to be capitalized or not (so it validates).
    
_participantMetrics = {
    
    "language": False,
    "ethnicity": False,
    "birthdate": False,
    "gender": True,
    "race": False,
    "disability": False,
    "description": False,
    "info": False, 
    "gestational age": False,
    "pregnancy term": True, 
    "birth weight": False
}


def assignParticipantMd(t, p, k, v):
    '''
    Set of routines to transform participant metadata, or pass it as is.
    t = the current list of all participant record being updated
    p = the current participant being update
    k = the string literal for the particpant metadata field
    v = the boolean value of whether it should be title cased or not 
    '''

    if k in p and p[k] != '':
        if k == "birthdate":
            t[k] = ch.ensureDateFormat(p[k].strip())
        elif k == "birth weight":
            t[k] = ch.lbsOzToGrams(p[k].strip())
        elif v == True:
            t[k] = p[k].capitalize().strip()
        else:
            t[k] = p[k].strip()


def getParticipantMap(p_csvFile):
    '''This will give us back a dictionary with participant IDs as keys and
        their records in the form of dictionaries as the values'''
    participantMap = {};
    p_reader = ch.giveMeCSV(p_csvFile)
    p_headers = p_reader.fieldnames
    
    for rec in p_reader:
        
        vals = {p_headers[z]: rec[p_headers[z]] for z in range(len(p_headers))}

        participantMap[rec['participantID']] = vals

    return participantMap

def getSessionMap(s_csvFile):
    '''This will give us back a dictionary where the unique session names (IDs) are associated with a dictionary of
       values containing participant'''

    r = ch.giveMeCSV(s_csvFile)
    rhead = r.fieldnames

    sessionMap = makeOuterMostElements(r)

    vol = ch.giveMeCSV(s_csvFile)
    vheaders = vol.fieldnames
    
    for i in vol:
        if 'participantID' in vheaders:
            participantID = i['participantID']
            sessionMap[i['key']]['records'].append({'ID': participantID, 'key': participantID, 'category': 'participant'})

    '''the following then deduplicates participants in any given containers participant record'''
    for k, v in sessionMap.items():
        deduped = list({d['ID']:d for d in sessionMap[k]['records']}.values())
        sessionMap[k]['records'] = deduped


    return sessionMap

def makeOuterMostElements(csvDictReader):
    '''make an empty dictionary with the session id for keys'''
    newdict = {}

    for n in csvDictReader:
        newdict[n['key']] = {'assets':[], 'records':[]}

    return newdict

def makeRecordsFromList(category, list_things, positions):
    ''' this function is to 1) make records for multiple records (e.g., tasks, exclusions) 
        2) help for positioning of records that might only apply to parts of a session 
        the category is just which type of record it is
        the list_things is the list of things (names of the record) ordered in a list 
        the positions are the cliptimes, to be orderd in the same sequence as the list_things and also ordered in a list
        NOTE: THIS IS PRETTY FRAGILE IT BEING BASED ON THE ASSUMPTION THAT BOTH LISTS ARE THE SAME LENGTH, WE CAN PUT IN A CHECK,
        BUT MAYBE THERE'S A BETTER WAY TO DO THIS.
    '''

    def check_time_format(cliptime):
        '''checks if a time is already milliseconds (isdigit()), if not it converts'''
        if cliptime.isdigit():
            return cliptime
        else:
            return ch.convertHHMMSStoMS(cliptime)

    recObjs = []
    
    position_formatted = []

    if positions is not None:
        #first check if there are the same amount of positions as there are records
        if len(list_things) != len(positions):
            print("You are trying to position records, but there are not enough positions per record or vice versa. check your data")
            sys.exit()
        
        for i in positions:
            clip = i.split('-')
            if clip[0] != '#':
                if clip[1] == '$':
                    position_formatted.append([str(check_time_format(clip[0])), None])
                else:
                    position_formatted.append([str(check_time_format(clip[0])), str(check_time_format(clip[1]))])


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
                    taskObj['positions'] = [position_formatted[i]]

            if not any(taskObj == d for d in recObjs):
                recObjs.append(taskObj)

        if category == 'exclusion':

            excl = list_things[i].strip()
            if excl != '#':
                exclObj = {'category':category, 
                           'reason':excl, 
                           'key':excl}
                if positions is not None:
                    exclObj['positions'] = position_formatted[i]
                recObjs.append(exclObj)

        if category == 'condition':

            cond = list_things[i].strip()
            condObj = {'category':category, 
                       'name':cond, 
                       'key':cond}
            recObjs.append(condObj)


    return recObjs

def recordAppend(obj, val, cat):
    ''' helper function for conditionally appending records as pilots (and perhaps others) dont have a 
        property (e.g., name) the others have.
    '''
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

    '''
       Here determine how to handle the positioning of assets:
       pos_start, pos_end, neg_start, neg_end
    '''

    def handleClipIns(pos):
        '''Handle all clip ins''' 
        clipArr = []   
        clip_ins = pos.split(';')
        num_of_clip_ins = len(clip_ins)

        for i in clip_ins:
            times = [str(check_time_format(j)) for j in i.split('-')]
            clipArr.append(tuple(times))

        return clipArr

    def handleClipOuts(neg):
        '''Handle all clip outs'''
        clipArr = []
        clip_outs = neg.split(';')
        num_of_clip_outs = len(clip_outs)

        if num_of_clip_outs == 1:
            times = [str(check_time_format(j)) for j in clip_outs[0].split('-')]
            time_in, time_out = times

            if time_in == '0': 
                clipArr.append((time_out, None))
            elif time_out == '$':
                clipArr.append(('0', time_in))
            else:
                clipArr.append(('0', time_in))
                clipArr.append((time_out, None))

        if num_of_clip_outs > 1:

            first_times = [str(check_time_format(j)) for j in clip_outs[0].split('-')]
            last_times = [str(check_time_format(j)) for j in clip_outs[-1].split('-')]
            mid_times = clip_outs[1:-1]

            first_in, first_out = first_times
            last_in, last_out = last_times

            if first_in != 0:
                clipArr.append(('0', first_in))

            if len(mid_times) == 0:

                if first_in == 0:
                    clipArr.append((first_out, last_in))
            
            if len(mid_times) > 0:
                recent = first_out
                for z in mid_times:
                    curr_clip = [str(check_time_format(j)) for j in z.split('-')]
                    curr_in, curr_out = curr_clip
                    clipArr.append((recent, curr_in))
                    recent = curr_out
                clipArr.append((curr_out, last_in))

            if last_out != '$':
                    clipArr.append((last_out, None))

        return clipArr


    pos, neg = args #one or more clips or None
    file_position = None if file_position == 'null' else file_position
    entries = []
    
    if pos == None and neg == None:
        clipArr = None


    if pos != None and pos != "":
        clipArr = handleClipIns(pos)
    else: 
        clipArr = None

    
    if neg != None and neg != "":
        clipArr = handleClipOuts(neg)
    else:
        clipArr = None

    
    if clipArr is not None:
        '''After handling in clip ins and/or clip outs, format them for returning to the map'''
        for i in clipArr:
            entries.append({'file': file_path,
                            'name': file_name, 
                            'position': i[0] if file_position is 'auto' or file_position == "" else file_position, 
                            'clip': list(i), 
                            'release': file_classification, 
                            'options': ""})

    else:
        entries.append({'file': file_path,
                        'name': file_name, 
                        'position': file_position, 
                        'release': file_classification, 
                        'options': ""})
    return entries

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

def format_files_for_ac(data):
    '''if the _assisted_curation arg is passed, that means we will need
       a property of "id" whose value is an integer for assets instead of "file". 
       This will add the "id" property, copy the value of "file" as int and delete "file"'''
    
    for r in data.items():
        for i in r[1]['assets']:
            i['id'] = int(i['file'])
            del i['file']
    return data

def mergeRecordPositions(data):
    '''this function merges records with the same key
       that also have positions so that all the positions 
       are segments in an array on one record object
    '''

    def dedupe(records):
        '''deduplicates records after being merged
        '''
        delist = []
        new = []
        for r in records:
            if r['key'] not in delist:
                delist.append(r['key'])
                new.append(r)
        return new


    for r in data.items():
        
        records = r[1]['records']
        l = []
        for d in records:
            for g in records:
                if d['key'] == g['key']:
                    if 'positions' in d and 'positions' in g:
                        if g['positions'][0] not in d['positions']:
                            d['positions'].append(g['positions'][0])
            
            l.append(d)
                
        r[1]['records'] = dedupe(l)

    return data
    
############################### MAIN PART OF SCRIPT THAT PARSES CSV TO JSON ####################################

def parseCSV2JSON(s_csvFile, p_csvFile):

    with open(s_csvFile, 'rt') as s_input:

        # some basic CSV preliminaries
        s_reader = csv.DictReader(s_input)
        s_headers = s_reader.fieldnames

        # if there is a participant file, get it, otherwise, just work with sessions
        if p_csvFile != None:
            p_map = getParticipantMap(p_csvFile)
        s_map = getSessionMap(s_csvFile)


        ### 
        # THIS IS WHERE IT LOOPS THROUGH THE CSV AND GATHERS UP AND PROCESSES EACH ROW
        ###
        for row in s_reader:

            name = row.get('name', None)
            key = row.get('key', name)
            top = True if 'top' in s_headers and row['top'] != '' else False
            dbrary_session_id = row.get('slot_id', None) #is this necessary anymore?
            if dbrary_session_id is not None:
                dbrary_session_id = int(dbrary_session_id) 
            s_curr = s_map[key]
            
            date = ch.assignIfThere('date', row, None)
            path = ch.assignIfThere('filepath', row, None)
            t_positions = ch.assignIfThere('task_positions', row, None)
            task_positions = t_positions.split(';') if t_positions is not None else t_positions
            ex_positions = ch.assignIfThere('excl_positions', row, None)
            excl_positions = ex_positions.split(';') if ex_positions is not None else ex_positions
            pilot = ch.assignIfThere('pilot', row, None)
            group = ch.assignIfThere('group', row, None)
            setting = ch.assignIfThere('setting', row, None)
            state = ch.assignIfThere('state', row, None)
            country = ch.assignIfThere('country', row, None)
            release = ch.assignIfThere('release', row, None)
            language = ch.assignIfThere('language', row, None)
            t_options = row['transcode_options'].split(' ') if 'transcode_options' in s_headers and row['transcode_options'] != '' else ''
            exclusion = makeRecordsFromList('exclusion', row['exclusion'].split(';'), excl_positions) if 'exclusion' in s_headers and row['exclusion'] != '' else ''
            condition = makeRecordsFromList('condition', row['condition'].split(';'), None) if 'condition' in s_headers and row['condition'] != '' else ''
            tasks = makeRecordsFromList('task', row['tasks'].split(';'), task_positions) if 'tasks' in s_headers and row['tasks'] != '' else ''

            context = {}
            context['category'] = 'context'
            context['key'] = 'context'
            if setting != None:
                context['setting'] = setting.title()
            if state != None:
                context['state'] = state.upper()
            if country != None:
                context['country'] = country
            if language != None:
                context['language'] = language.title()


            

            for i in range(len(s_headers)):
                header = s_headers[i].strip()

                #TODO: CLEAN UP EVERYTHING IN THIS LOOP.

                if header == 'participantID':
                    for i in range(len(s_curr['records'])):
                        target = list(s_curr['records'])[i]

                        '''missing: date and age, in days.'''
                        if 'category' in target and target['category'] == 'participant' and target['ID'] != '':

                            p_target = p_map[target['ID']]

                            for _k, _v in _participantMetrics.items():
                                assignParticipantMd(target, p_target, _k, _v)

                elif 'file_' in header and row[header] != '':
                    if path != None:
                        fpath = os.path.join(path, row[header])
                    else:
                        fpath = row[header]
                    ##### CLIP STUFF #####
                    asset_no = header.split("_")[1]
                    pos_clip = "clip_in_" 
                    neg_clip = "clip_out_" 
                    file_name = "fname_" + asset_no
                    file_position = "fposition_" + asset_no
                    file_classification = "fclassification_" + asset_no
                    fname = ch.assignEmptyVals(file_name, row, None)
                    fposition = row.get(file_position, 'auto')
                    fclassification = row.get(file_classification, None)
                    prefixes = (pos_clip, neg_clip)
                    clip_options = tuple(ch.assignIfThere(j+asset_no, row, None) for j in prefixes)
            
                    asset_entry = checkClipsStatus(fpath, fname, fposition, fclassification, *clip_options) #sends either 1 or more sets of clips or none to get formatted

                    for z in asset_entry:
                        z['release'] = fclassification.upper() if fclassification is not None else None

                        if t_options != '':
                            z['options'] = t_options
                        else:
                            del z['options']
                        z['position'] = fposition if z['position'] == '' else z['position']
                        if z['name'] is None:
                            del z['name']
                        if z not in s_curr['assets']:
                            s_curr['assets'].append(z)

                    ##### END CLIP STUFF #####

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

                elif header in _contextMetrics and len(context) > 2 and not any(context == d for d in s_curr['records']):
                    s_curr['records'].append(context)

                elif header == 'tasks' and tasks != '':
                    for task in tasks:
                        if not any(task == f for f in s_curr['records']):
                            s_curr['records'].append(task)

                if date is not None:
                    s_curr['date'] = ch.ensureDateFormat(date)

                if dbrary_session_id is not None:
                    s_curr['id'] = dbrary_session_id

                #container level properties
                s_curr['top'] = top
                s_curr['name'] = name 
                if key is not None:
                    s_curr['key'] = key
                s_curr['release'] = release.upper() if release is not None else None
                
                if 'release' not in s_headers:
                    del s_curr['release'] # delete release if there was no release colume in ingest session spreadsheet

                if s_curr['name'] is None:
                    del s_curr['name'] #delete container file name if added and None
        ### 
        # // THIS IS WHERE IT STOPS LOOPING THROUGH THE CSV, GATHERING UP AND PROCESSING EACH ROW
        ###


        #if --assisted flag is raised, format the file property to be id and an int
        if _assisted_curation:
           s_map = format_files_for_ac(s_map)


        #make sure multiple record objects are merged into one re: positions   
        s_map = mergeRecordPositions(s_map) 


        #create the final datascructure by wrapping it all in a dictionary, giving it a name property, and sort the containers (sessions) by key
        data = {
            'name': _volume_name,
            'containers': sorted(list(s_map.values()), key=key_checker)
        }



    #convert final data to JSON
    res = json.dumps(data, indent=4)

    #create the output file and save JSON output there.
    output_dest = '../output/' + _filepath_prefix + '_output.json'
    j = open(output_dest, 'wt')
    j.write(res)




if __name__ == '__main__':
    parseCSV2JSON(_session_csv, _participant_csv)
