import csv
import csv_helpers as ch
import time
import sys

DVYU_OUTPUT = sys.argv[1] #datavyu file that you want to convert to a set of columns for csv2json.py
PATH_PARTS = DVYU_OUTPUT.split('/')
PATH_PARTS.pop()
PATH = ('/').join(PATH_PARTS)
DBRY_OUTPUT = PATH+'/'+DVYU_OUTPUT.split('/')[-1].split('.')[0]+'_dbrary.csv'
RECORD_CATEGORY = sys.argv[2] + '_' #record we are compiling here (e.g. task, exclusion, etc.)
fformat = DVYU_OUTPUT.split('.')[-1]

def convertMStoMMHH(milliseconds):
    clip_time = int(milliseconds) * 0.001 
    return time.strftime('%H:%M:%S', time.gmtime(clip_time))

def convert(f):
    output = open(DBRY_OUTPUT, 'w')
    output_headers = ['key', 'condition', 'tasks', 'task_positions']
    csvoutput = csv.writer(output)
    csvoutput.writerow(output_headers)
    
    csvinput = ch.giveMeTSV(f) if fformat == 'tsv' else ch.giveMeCSV(f)
    h = next(csvinput)
    hIdx = ch.getHeaderIndex(h)

    
    for row in csvinput:
        session_key = ch.assignIfThere('key', hIdx, row, None)
        condition = row[hIdx['condition']]
        records = []
        clips = []

        for i in range(len(h)):
            header = ch.cleanVal(h[i])


            if RECORD_CATEGORY in header and row[i] != '':
                record = row[i]
                record_no = header.split('_')[1]
                on = 'onset_'+record_no
                off = 'offset_'+record_no
                clip = convertMStoMMHH(row[hIdx[on]])+'-'+convertMStoMMHH(row[hIdx[off]])

                records.append(row[i])
                clips.append(clip)


        csvoutput.writerow([session_key, 
                           condition, 
                           (';').join(records), 
                           (';').join(clips)])


    
if __name__ == '__main__':
    convert(DVYU_OUTPUT)
