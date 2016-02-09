import csv
import csv_helpers as ch
import sys

'''short script to check whether onset times happen before offset times. nothing more, nothing less'''


input = sys.argv[1]
csv_data = ch.giveMeCSV(input)
headers = next(csv_data)
hIdx = ch.getHeaderIndex(headers)
for row in csv_data:
    for i in headers:
        if 'task_' in i:
            curr_h = i
            curr_no = curr_h.split("_")[1]
            curr_on = "onset_" + curr_no
            curr_off = "offset_" + curr_no
            curr_onset = row[hIdx[curr_on]]
            curr_offset = row[hIdx[curr_off]]
            print("now we are on %s_%s: %s - %s" % (row[hIdx['id']], curr_no, ch.convertMStoHHMM(curr_onset), ch.convertMStoHHMM(curr_offset)))
            if int(curr_onset) > int(curr_offset):
                print(row[hIdx['id']], "has a problem", curr_on, ":", row[hIdx[curr_on]] , "is greater than", curr_off, ":", row[hIdx[curr_off]])


