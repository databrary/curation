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
            s_dropdowns = {
                'exclusion':record_field_values['reason']['enum'],
                'fclassification_1':volume_field_values['release']['enum'],
                'fclassification_2':volume_field_values['release']['enum'],
                'setting':record_field_values['setting']['enum'],
                'state':record_field_values['state']['enum'],
                'consent':volume_field_values['release']['enum']
            }

            for k,v in s_dropdowns.items():
                wsheet.data_validation(1, headerIdx[k], 1000, headerIdx[k], {'validate': 'list', 'source':v})
            
        if curr_sheet =='participants':
            p_dropdowns = {
                'race':record_field_values['race']['enum'],
                'gender':record_field_values['gender']['enum'],
                'ethnicity':record_field_values['ethnicity']['enum'],
                'pregnancy term':record_field_values['pregnancy term']['enum']
            }
            
            for k,v in p_dropdowns.items():
                wsheet.data_validation(1, headerIdx[k], 1000, headerIdx[k], {'validate': 'list', 'source':v})

    wbook.close()


'''first make csv'''
csvWriter(_PATH_TO_TEMPLATES+_SESSIONS_TEMPLATE, fields.General.session_headers)
csvWriter(_PATH_TO_TEMPLATES+_PARTICIPANTS_TEMPLATE, fields.General.participant_headers)
'''then make corresponding xlsx files'''
xlsxWriter(_PATH_TO_TEMPLATES)
