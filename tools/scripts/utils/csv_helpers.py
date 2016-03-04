import csv
import sys
import time

################### QUICK OPERATIONS FOR REDUNDANT TASKS INVOLVING CSVs ###############################
def giveMeTSV(file):
    t = open(file, 'rt')
    return csv.reader(t, delimiter='\t')

def giveMeCSV(csvfile):
    f = open(csvfile, 'rt') 
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

def makeNewFile(path, filename_addition="_output"):
    '''given a filepath as an argument, we will use that to create the new file where
       output will be stored'''
    PATH_PARTS = path.split('/')
    PATH_PARTS.pop()
    PATH = ('/').join(PATH_PARTS)
    return PATH+'/'+path.split('/')[-1].split('.')[0]+filename_addition+'.csv'

def parseHHMMSS(hms):
    l = hms.split(':')
    if hms == "$":
        return hms
    elif len(l) == 3:
        h, m, s = l
    elif len(l) == 2:
        h = 0
        m, s = l
    if "." in s:
       s = s.split('.')[0]
    return (h, m, s)

def convertHHMMtoS(hms):
    '''take a time in the form of HH:MM:SS or MM:SS and return a rounded int for seconds'''
    h, m, s = parseHHMMSS(hms)
    return int(h) * 3600 + int(m) * 60 + int(s)

def convertHHMMSStoMS(hms):
    '''take a time in the form of HH:MM:SS or MM:SS and return a rounded int for milliseconds'''
    h, m, s = parseHHMMSS(hms)
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000


def convertMStoHHMM(ms):
    clip_time = int(ms) * 0.001 
    return time.strftime('%H:%M:%S', time.gmtime(clip_time))

def convertStoHHMM(seconds):
    '''returns string of HH:MM:SS from a seconds integer)'''
    if seconds == "$":
        return seconds

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)

def findHalfTime(t):
    '''for now takes a time sting in the form of HH:MM:SS.mm and gives you back the halfway point in same format'''
    s = convertHHMMtoS(t)
    half = s / 2
    return convertStoHHMM(half)

def leftJoinCSV(file1, file2, *args):
    '''Really should only be used to left join two csv files. Left file is first arg, right file is second arg.
       Column(s) title (string in the head) are the third and fourth args'''
    if len(args) > 1:
        '''can either enter one column for both or each one ''' 
        column1 = args[0]
        column2 = args[1]
    elif len(args) == 1:
        column1 = args[0]
        column2 = args[0]
    
    f1csv = giveMeCSV(file1)
    f2csv = giveMeCSV(file2)
    f1head = next(f1csv)
    f2head = next(f2csv)
    f1Idx = getHeaderIndex(f1head)
    f2Idx = getHeaderIndex(f2head)
    newFile = makeNewFile(file1)
    merged = csv.writer(open(newFile, 'w'))
    merged.writerow(f1head+f2head)

    right_indexed = {row[f2Idx[column2]].strip(): row for row in f2csv}
    
    for row1 in f1csv:
        if row1[f1Idx[column1]].strip() in right_indexed.keys():
            mrow = row1 + right_indexed[row1[f1Idx[column1]]]
        else:
            mrow = row1
        merged.writerow(mrow)    

def leadingZeros(csvfile, zeros, col="participantID", newCol="pID" ):
    '''use this if you have a csv file where the IDs are interpretted as numbers when you want
       them to be strings. That is, you need leading zeros and programs like libre office make you 
       want to throw yourself out of a window trying to achieve and maintain that formatting over
       a number of different use cases'''
    num_converter = "%0" + str(zeros) + "d"
    new_filename = makeNewFile(csvfile, "_zeroed")
    fcsv = giveMeCSV(csvfile)
    fhead = output_head = next(fcsv)
    output_head.extend([newCol])
    fcsvIdx = getHeaderIndex(fhead)
    output_file = csv.writer(open(new_filename, 'w'))
    output_file.writerow(output_head)
    for row in fcsv:
        non_zeroed_id = int(row[fcsvIdx[col]])
        zeroed_id = str(num_converter % (non_zeroed_id))
        row.extend([zeroed_id])
        output_file.writerow(row)

def filterCSV(csvfile1, csvfile2, col="participantID"):
    '''use this for comparing two csvfiles, and filtering out the rows that are already in both of them
       csvfile1 is the file with the structure you want to keep, and csvfile2 is what you want to compare it to'''
    new_filename = makeNewFile(csvfile1, "_filtered")
    f1csv = giveMeCSV(csvfile1)
    f2csv = giveMeCSV(csvfile2)
    f1head = next(f1csv)
    f2head = next(f2csv)
    f1Idx = getHeaderIndex(f1head)
    f2Idx = getHeaderIndex(f2head)
    output_file = csv.writer(open(new_filename, 'w'))
    output_file.writerow(f1head)
    filtervals = [r[f2Idx[col]].strip() for r in f2csv]
    
    for row1 in f1csv:
        p = row1[f1Idx[col]].strip()     
        if p not in filtervals:
            output_file.writerow(row1)