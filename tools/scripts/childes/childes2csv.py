import csv
import os
import sys
import glob
sys.path.append('../utils')
import fields

input_directory = sys.argv[1] #provide the main directory where all the files are
file_input = sys.argv[2] #give a namespace for this - ie: childes
output_path = '../../i/'


p_file = output_path + file_input + '_p' + '.csv'
s_file = output_path +  file_input + '_s' + '.csv'
        

def getFilePath(directory):
    filepaths = []
    print 'getting filepaths...'
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            filepath = glob.glob(os.path.join(subdir, '*.cha'))

            filepaths += filepath

    return filepaths


def getSessions(f, directory, fpath):
    s_list = {}

    print 'getting out the sessions'
    for i in fpath:

        fpath_list = i.split('/')

        asset = fpath_list[-1].split('.')[0]
        
        fpath_list.pop()

        asset_path = '/'.join(fpath_list)

        s_list[asset] = {}

        if os.path.isfile(i):

            with open(i, 'rb') as chafile:

                data = chafile.readlines()

                for line in data:
                    if line.startswith('@') and 'Date' in line:
                        session_date = line.split('\t')[1]
                        s_list[asset]['date'] = session_date.strip()

                    if line.startswith('@') and 'Languages' in line:
                        language = line.split('\t')[1]
                        s_list[asset]['language'] = language.strip()

                    if line.startswith('@') and 'ID' in line and 'CHI' in line:
                        participant = line.split('\t')[1].split('|')[1]
                        s_list[asset]['participant'] = participant.strip()

                    if line.startswith('@') and 'Media' in line:
                        asset_val = line.split('\t')[1].split(',')

                        if asset_val[1].strip() == 'audio':
                            asset_file = asset_val[0] + '.mp3'
                            s_list[asset]['file'] = asset_file.strip()
                        if asset_val[1].strip() == 'video':
                            asset_file = asset_val[0] + '.mov'
                            s_list[asset]['file'] = asset_file.strip()

                        
                s_list[asset]['path'] = asset_path
                    
    print 'sessions got'
    return s_list


                    
def getParticipants(f, directory, fpath):

    p_list = {}

    print 'getting out the participants'
    for i in fpath:

        if os.path.isfile(i):

            with open(i, 'rb') as chafile:

                data = chafile.readlines()

                for line in data:
                    if line.startswith('@') and 'ID' in line and 'CHI' in line:
                        participant = line.split('\t')[1].split('|')

                        p_list[participant[1]] = {'language': participant[0], 'gender': participant[4]}

                    if line.startswith('@') and 'Birth of CHI' in line:
                        dob = line.split('\t')[1].strip()
                        p_list[participant[1]]['birthdate'] = dob


    print 'got the participants'
    return p_list

def makeParticipantCSV(csvfile, participant_dictionary, headers):
    with open(csvfile, 'wb') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        
        for k,v in participant_dictionary.items():
            participantID = k
            birthdate = v['birthdate']
            gender = v['gender']
            race = ''
            ethnicity = ''
            language_1 = v['language']
            language_2 = ''
            disability = ''
            consent = ''

            outfile.writerow([participantID,birthdate,gender,race,ethnicity,language_1,language_2,disability,consent])


def makeSessionCSV(csvfile, session_dictionary, headers):
    with open(csvfile, 'wb') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        
        for k,v in session_dictionary.items():
            name = k 
            date = v['date'] 
            top = ''
            pilot = '' 
            exclusion = '' 
            classification = '' 
            filename = v['path'] + '/' + v['file']
            participantID = v['participant']
            segment_in = ''
            segment_out = ''
            condition = ''
            group = ''
            language = v['language']
            setting = ''
            state = ''
            country = ''
            info = ''

            outfile.writerow([name, date, top, pilot, exclusion , classification, filename, participantID, segment_in, segment_out, condition, group, language, setting, state, country, info])



if __name__ == "__main__":

    participant_dict = getParticipants(p_file, input_directory, getFilePath(input_directory))
    session_dict = getSessions(s_file, input_directory, getFilePath(input_directory))

    makeParticipantCSV(p_file, participant_dict, fields.participant_headers)
    makeSessionCSV(s_file, session_dict, fields.session_headers)


