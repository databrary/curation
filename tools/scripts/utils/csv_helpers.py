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
