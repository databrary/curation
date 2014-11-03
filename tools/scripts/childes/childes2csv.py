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

def makeCSV(filename, headers):
    with open(filename, 'wb') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)

makeCSV(p_file, fields.participant_headers)
makeCSV(s_file, fields.session_headers)

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


        print asset_path

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
                        p_list[participant[1]]['birtdate'] = dob


    print 'got the participants'
    return p_list



participant_dict = getParticipants(p_file, input_directory, getFilePath(input_directory))
sessions_dict = getSessions(s_file, input_directory, getFilePath(input_directory))

print participant_dict
print sessions_dict



