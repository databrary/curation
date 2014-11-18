import csv
import fields

_PATH_TO_TEMPLATES = '../../../spec/templates/'
_SESSIONS_TEMPLATE = 'sessions_template.csv'
_PARTICIPANTS_TEMPLATE = 'participants_template.csv'



def csvWriter(path, headers):
    with open(path, 'wt') as csvfile:
        outfile = csv.writer(csvfile, delimiter = ',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
        outfile.writerow(headers)
        csvfile.close()


csvWriter(_PATH_TO_TEMPLATES+_SESSIONS_TEMPLATE, fields.General.session_headers)
csvWriter(_PATH_TO_TEMPLATES+_PARTICIPANTS_TEMPLATE, fields.General.participant_headers)

