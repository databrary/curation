import csv
import json
import fields
import os, glob
import sys
try:
    from xlsxwriter.workbook import Workbook
except:
    print("Couldn't load xlsxwriter because you're not in acceptable virtual environment. Switch to venv2 or run `pip install xlsxwriter`")
    sys.exit()

_PATH_TO_TEMPLATES = '../../../spec/templates/'
_SESSIONS_TEMPLATE = 'sessions_template.csv'
_PARTICIPANTS_TEMPLATE = 'participants_template.csv'

volume_schema = json.loads(open('../../../spec/volume.json', 'rt').read())
volume_field_values = volume_schema['definitions']
container_field_values = volume_schema['definitions']['container']
record_field_values = volume_schema['definitions']['record']['properties']


def headerIndices(headers):

    hIndex = {headers[i]: i for i in range(len(headers))}

    return hIndex


def csvWriter(path, headers):
    with open(path, 'wt') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)

        csvfile.close()


def xlsxWriter(path):
    project = '../../../spec/templates/ingest_template'
    wbook = Workbook(project + '.xlsx')

    for csvfile in glob.glob(os.path.join(_PATH_TO_TEMPLATES, '*.csv')):
        curr_sheet = csvfile.split('/')[-1].split('_')[0]

        if curr_sheet == 'sessions':
            headerIdx = headerIndices(fields.General.session_headers)
        elif curr_sheet == 'participants':
            headerIdx = headerIndices(fields.General.participant_headers)

        wsheet = wbook.add_worksheet(curr_sheet)

        with open(csvfile, 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    wsheet.write(r, c, col)

        if curr_sheet == 'sessions':
            wsheet.data_validation(1, headerIdx['exclusion'], 1000, headerIdx['exclusion'], {'validate': 'list', 'source': record_field_values['reason']['enum']})
            wsheet.data_validation(1, headerIdx['fclassification_1'], 1000, headerIdx['fclassification_1'], {'validate': 'list', 'source': volume_field_values['release']['enum']})
            wsheet.data_validation(1, headerIdx['fclassification_2'], 1000, headerIdx['fclassification_2'], {'validate': 'list', 'source': volume_field_values['release']['enum']})
            wsheet.data_validation(1, headerIdx['setting'], 1000, headerIdx['setting'], {'validate': 'list', 'source': record_field_values['setting']['enum']})
            wsheet.data_validation(1, headerIdx['state'], 1000, headerIdx['state'], {'validate': 'list', 'source': record_field_values['state']['enum']})
            wsheet.data_validation(1, headerIdx['consent'], 1000, headerIdx['consent'], {'validate': 'list', 'source': volume_field_values['release']['enum']})

        if curr_sheet =='participants':
            wsheet.data_validation(1, headerIdx['race'], 1000, headerIdx['race'], {'validate': 'list', 'source': record_field_values['race']['enum']})
            wsheet.data_validation(1, headerIdx['gender'], 1000, headerIdx['gender'], {'validate': 'list', 'source': record_field_values['gender']['enum']})
            wsheet.data_validation(1, headerIdx['ethnicity'], 1000, headerIdx['ethnicity'], {'validate': 'list', 'source': record_field_values['ethnicity']['enum']})



    wbook.close()



'''first make csv'''
csvWriter(_PATH_TO_TEMPLATES+_SESSIONS_TEMPLATE, fields.General.session_headers)
csvWriter(_PATH_TO_TEMPLATES+_PARTICIPANTS_TEMPLATE, fields.General.participant_headers)
'''then make corresponding xlsx files'''
xlsxWriter(_PATH_TO_TEMPLATES)
