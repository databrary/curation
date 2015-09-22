import csv
import sys, os
import csv_helpers as ch

'''This script will take two .csv files, one is the original ingest sessions csv.
   The other is the update ingest sheet (e.g. a csv crafted from datavyu output)
   We compare the update ingest sheet with the original ingest sheet and divide the  
   ingest update into two spreadsheets, one which is only the sessions that were in the
   original and the other is those not in the original.'''

original_file = sys.argv[1]
update_file = sys.argv[2]

ingest_orig = ch.giveMeCSV(original_file) 
ingest_update = ch.giveMeCSV(update_file)

incl_filepath = ch.makeNewFile(update_file, '_included')
excl_filepath = ch.makeNewFile(update_file, '_excluded')

incl_output  = csv.writer(open(incl_filepath, 'w'))
excl_output = csv.writer(open(excl_filepath, 'w'))

headers_o = next(ingest_orig)
headers_u = next(ingest_update)

hIdx_o = ch.getHeaderIndex(headers_o)
hIdx_u = ch.getHeaderIndex(headers_u)

incl_output.writerow(headers_u)
excl_output.writerow(headers_u)



if __name__ == '__main__':
    for row_o in ingest_orig:
        for row_u in ingest_update:
            if row_u[hIdx_u['key']] == row_o[hIdx_o['key']]:
                incl_output.writerow(row_u)
                break
            else:
                excl_output.writerow(row_u)
                


