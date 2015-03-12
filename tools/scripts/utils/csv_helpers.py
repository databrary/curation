import csv
import sys


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

def mergeCSV(file1, file2, *args):
    
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
    merged = csv.writer(open('merged.csv', 'w'))
    merged.writerow(f1head+f2head)
    
    for row1 in f1csv:
        for row2 in f2csv:
            if row1[f1Idx[column1]] == row2[f2Idx[column2]]:
                row_merged = row1+row2
                merged.writerow(row_merged)
                break

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







                