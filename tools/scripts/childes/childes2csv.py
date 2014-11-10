import csv
import os
import sys
import glob
import datetime
sys.path.append('../utils')
from fields import Childes, General


rel_path = sys.argv[1] #provide the main directory where all the files are
file_input = sys.argv[2] #give a namespace for this - ie: childes
fixed_path = '../../../data/'
input_directory = fixed_path + rel_path
output_path = '../../i/'


p_file = output_path + file_input + '_p' + '.csv'
s_file = output_path +  file_input + '_s' + '.csv'

def dateFromString(datestring):
    '''This will take a date in the form of 04-DEC-2000 and change to a string of 2000-12-03'''
    date_result = datetime.datetime.strptime(datestring, "%d-%b-%Y")
    date_result = date_result.strftime("%Y-%m-%d")
    return date_result

def getDaysFromDates(birthdate, sessiondate):
    '''This will take two date strings like 2000-12-04 and create a date object for calculating days'''
    d0 = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
    d1 = datetime.datetime.strptime(sessiondate, "%Y-%m-%d")

    diff = d1 - d0

    return diff.days
        

def getFilePath(directory):
    filepaths = []
    print('getting filepaths...')
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            filepath = glob.glob(os.path.join(subdir, '*.cha'))

            filepaths += filepath

    return filepaths

def getAssets(directory):
    '''currently not using this, but might come in handy to generalize in refactoring'''

    assets0 = {}
    for subdir, dirs, files in os.walk(directory):
        for d in dirs:
            for files in os.walk(directory + "/" + d):
                assets0[d] = files[2]


    assets_map = {}
    all_assets = []
    for k,v in assets0.items():
        assets_map[k] = {}
        for i in range(len(v)):
            currSesh = v[i].split('.')[0]
            assets_map[k][currSesh] = []
            all_assets.append(v[i])
            
            
    for k,v in assets_map.items():
        for j in range(len(all_assets)):
            for s in range(len(v.keys())):
            
                if v.keys()[s] in all_assets[j]:
                    assets_map[k][v.keys()[s]].append(all_assets[j])

            

    return assets_map


def getSessions(f, directory, fpath):
    s_list = {}

    print('getting out the sessions')
    for i in fpath:

        fpath_list = i.split('/')
        asset = fpath_list[-1].split('.')[0]
        
        s_list[asset] = {}

        if os.path.isfile(i):

            with open(i, 'rt') as chafile:

                data = chafile.readlines()

                for line in data:
                    if line.startswith('@') and 'Date' in line:
                        session_date = line.split('\t')[1].strip()
                        s_list[asset]['date'] = dateFromString(session_date)

                    if line.startswith('@') and 'Languages' in line:
                        language = Childes.language_map[line.split('\t')[1].strip()]
                        s_list[asset]['language'] = language

                    if line.startswith('@') and 'ID' in line and 'CHI' in line:
                        participant = line.split('\t')[1].split('|')[1].strip()
                        s_list[asset]['participant'] = participant              

                    if line.startswith('@') and 'Media' in line:
                        asset_val = line.split('\t')[1].split(',')

                        if asset_val[1].strip() == 'audio':
                            asset_file = asset_val[0] + '.mp3'
                            s_list[asset]['file'] = asset_file.strip()
                        if asset_val[1].strip() == 'video':
                            asset_file = asset_val[0] + '.mov'
                            s_list[asset]['file'] = asset_file.strip()

                        s_list[asset]['transcript'] = asset_val[0] + '.cha'

                s_list[asset]['path'] = rel_path if rel_path.endswith('/') else rel_path + '/' 
                    
    print('sessions got')
    return s_list
                    
def getParticipants(f, directory, fpath):

    p_list = {}

    print('getting out the participants')
    for i in fpath:

        if os.path.isfile(i):

            with open(i, 'rt') as chafile:

                data = chafile.readlines()

                for line in data:
                    if line.startswith('@') and 'ID' in line and 'CHI' in line:
                        participant = line.split('\t')[1].split('|')
                        language = Childes.language_map[participant[0]]
                        gender = participant[4]

                        p_list[participant[1]] = {'language': language, 'gender': gender}

                    if line.startswith('@') and 'Birth of CHI' in line:
                        dob = line.split('\t')[1].strip()
                        p_list[participant[1]]['birthdate'] = dateFromString(dob)

                    if line.startswith('@') and 'Date' in line:
                        session_date = line.split('\t')[1].strip()
                        p_list[participant[1]]['date'] = dateFromString(session_date)


    print('got the participants')
    return p_list



def makeParticipantCSV(csvfile, participant_dictionary, headers):
    with open(csvfile, 'wt') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        
        for k,v in participant_dictionary.items():
            participantID = k
            birthdate = v['birthdate']
            date = v['date']
            age_days = getDaysFromDates(v['birthdate'], v['date'])
            gender = v['gender']
            race = ''
            ethnicity = ''
            language = v['language']
            disability = ''
            category = 'participant'
            consent = ''

            outfile.writerow([participantID,birthdate,date,age_days,gender,race,ethnicity,language,disability,category,consent])


def makeSessionCSV(csvfile, session_dictionary, headers):
    with open(csvfile, 'wt') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        
        for k,v in session_dictionary.items():
            name = k 
            date = v['date'] 
            top = ''
            pilot = '' 
            exclusion = '' 
            classification = ''
            path = v['path'] 
            filename = v['file']
            transcript = v['transcript']
            participantID = v['participant']
            clip_in = ''
            clip_out = ''
            position = ''
            condition = ''
            group = ''
            language = v['language']
            setting = ''
            state = ''
            country = ''
            consent = ''


            outfile.writerow([name, date, participantID, top, pilot, exclusion , classification, clip_in, clip_out, position, path, filename, transcript, condition, group, language, setting, state, country, consent])



if __name__ == "__main__":

    participant_dict = getParticipants(p_file, input_directory, getFilePath(input_directory))
    session_dict = getSessions(s_file, input_directory, getFilePath(input_directory))

    makeParticipantCSV(p_file, participant_dict, General.participant_headers)
    makeSessionCSV(s_file, session_dict, General.session_headers)

    

