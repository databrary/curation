import csv
import os, sys
import csv_helpers as c
from collections import OrderedDict

_FILE = sys.argv[1]

def makeData(input):
    f = c.giveMeCSV(input)
    fhead = next(f)
    fIndx = c.getHeaderIndex(fhead)
    return {row[fIndx['participantID']]:[] for row in f}

f = c.giveMeCSV(_FILE)
fhead = next(f)
fIndx = c.getHeaderIndex(fhead)
output_filename = c.makeNewFile(_FILE, '_formatted')
output = csv.writer(open(output_filename, 'w'))
output_header = ['participantID', 'file1', 'task1', 'dur1', 'file2', 'task2', 'dur2']
output.writerow(output_header)

data = makeData(_FILE) 

for row in f:
    data[row[fIndx['participantID']]].append(row[fIndx['FILE']])
    data[row[fIndx['participantID']]].append(row[fIndx['TASK']])
    data[row[fIndx['participantID']]].append(row[fIndx['DURATION_M']])

data = OrderedDict(sorted(data.items())) 

for k,v in data.items():
    v.insert(0, k)
    output.writerow(v)


