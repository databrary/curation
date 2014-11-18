import csv
import fields
import os, glob
from xlsxwriter.workbook import Workbook

_PATH_TO_TEMPLATES = '../../../spec/templates/'
_SESSIONS_TEMPLATE = 'sessions_template.csv'
_PARTICIPANTS_TEMPLATE = 'participants_template.csv'



def csvWriter(path, headers):
    with open(path, 'wt') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        csvfile.close()


def xlsxWriter(path):
    project = '../../../spec/templates/ingest_template'
    wbook = Workbook(project + '.xlsx')

    for csvfile in glob.glob(os.path.join(_PATH_TO_TEMPLATES, '*.csv')):

        wsheet = wbook.add_worksheet(csvfile.split('/')[-1].split('_')[0])
        with open(csvfile, 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    wsheet.write(r, c, col)
    wbook.close()



'''first make csv'''
csvWriter(_PATH_TO_TEMPLATES+_SESSIONS_TEMPLATE, fields.General.session_headers)
csvWriter(_PATH_TO_TEMPLATES+_PARTICIPANTS_TEMPLATE, fields.General.participant_headers)
'''then make corresponding xlsx files'''
xlsxWriter(_PATH_TO_TEMPLATES)