import csv
import sys


################### QUICK OPERATIONS FOR REDUNDANT TASKS INVOLVING CSVs ###############################
def giveMeTSV(file):
    t = open(file, 'rt')
    return csv.reader(t, delimiter='\t')

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

def makeNewFile(path, filename_addition="output"):
    '''given a filepath as an argument, we will use that to create the new file where
       output will be stored'''
    PATH_PARTS = path.split('/')
    PATH_PARTS.pop()
    PATH = ('/').join(PATH_PARTS)
    return PATH+'/'+path.split('/')[-1].split('.')[0]+filename_addition+'.csv'

def mergeCSV(file1, file2, *args):

    if len(args) > 1:
        '''can either enter one column for both or each one ''' 
        column1 = args[0]
        column2 = args[2]
    elif len(args) == 1:
        column1, column2 = args[0]

    f1 = open(file1, 'rt')
    f2 = open(file2, 'rt')
    f1head = next(f1)
    f2head = next(f2)
    f1Idx = getHeaderIndex(f1head)
    f2Idx = getHeaderIndex(f2head)

    f1csv = giveMeCSV(f1)
    f2csv = giveMeCSV(f2)

    merged = csv.writer(open('merged.csv', 'w'))
    merged.writerow(f1head+f2head)

    for row1 in f1:
        for row2 in f2:
            if row1[hIdx_u[column1]] == row2[hIdx_o[column2]]:
                row_merged = row1+row2
                mergred.writerow(row_merged)

    merged.close()
                