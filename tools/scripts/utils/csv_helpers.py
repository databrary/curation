import csv
import sys
import time

################### QUICK OPERATIONS FOR REDUNDANT TASKS INVOLVING CSVs ###############################

### CSV IO

def giveMeTSV(file): #iohelper
    t = open(file, 'rt')
    return csv.DictReader(t, delimiter='\t')

def giveMeCSV(csvfile): #iohelper
    f = open(csvfile, 'rt') 
    return csv.DictReader(f)

def cleanVal(i):
    return i.strip()

def makeNewFile(path, filename_addition="_output"): #iohelper
    '''given a filepath as an argument, we will use that to create the new file where
       output will be stored'''
    PATH_PARTS = path.split('/')
    PATH_PARTS.pop()
    PATH = ('/').join(PATH_PARTS)
    return PATH+'/'+path.split('/')[-1].split('.')[0]+filename_addition+'.csv'


### STRINGS

def assignIfThere(k, row, assignthis): #stringhelper
    '''all purpose check for key in csv.DictReader instance (row) so we know to assign a value for the row or not
        so we do not need empty columns in the spreadsheet'''

    return row[k] if k in row.keys() and row[k] != '' else assignthis

### TIME

def parseHHMMSS(hms): #timehelper
    l = [x.strip() for x in hms.split(':')]
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


def convertHHMMSStoMS(hms): #timehelper
    '''take a time in the form of HH:MM:SS or MM:SS and return a rounded int for milliseconds'''
    h, m, s = parseHHMMSS(hms)
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000

def findHalfTime(t): #timehelper
    '''for now takes a time sting in the form of HH:MM:SS.mm and gives you back the halfway point in same format'''
    ms = convertHHMMSStoMS(t)
    half = ms / 2
    return convertMStoHHMMSS(half)

def lbsOzToGrams(weight):
    '''right now assumes a string in the format ## lb. ## oz.'''
    weight.lower()
    if weight.strip() != '':
        if 'lb.' in weight and 'oz.' in weight: 
            arr = weight.strip().split(' ')
            arr = [i for i in arr if i != 'lb.' and i != 'oz.']
            pounds, ounces = arr
            lbs = float(pounds)
            ozs = float(ounces)
            gsinlbs = 453.592
            gsinozs = 28.3495
            lbs2gs = lbs * gsinlbs
            ozs2gs = ozs * gsinozs

            return str(int(lbs2gs + ozs2gs))
        else: 
            print("Think there's an issue with weights in the data")
            sys.exit()
    else:
        return None

def ensureDateFormat(date):
    '''function to convert all mm/dd/yyyy dates into yyyy-mm-dd, 
       although quite honestly this should be done before utilizing this script
    '''
    if '/' in date:
        date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    return date


  


